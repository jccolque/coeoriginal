#Imports de python
import copy
import json
import logging
from base64 import b64decode
from datetime import timedelta
#Imports de Django
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
#Imports del proyecto
from coe.constantes import LAST_DATETIME
from operadores.models import Operador
from georef.models import Nacionalidad, Localidad
#Imports de la app
from .choices import TIPO_PERMISO
from .models import Individuo, AppData, Domicilio, GeoPosicion
from .models import Atributo, Sintoma, Situacion, Seguimiento
from .models import Permiso
from .tokens import TokenGenerator
from .geofence import controlar_distancia

#Definimos logger
logger = logging.getLogger("apis")

@require_http_methods(["GET"])
def IdeConfig(request):
    return JsonResponse(
        {
            "action":"IdeConfig",
            #WebServices
            "WebServices":
            {
                "localidad": reverse("georef:localidad-autocomplete"),
                "barrio": reverse("georef:barrio-autocomplete"),
                "estados": reverse('ws_urls:tipo_estado'),
                "conductas": reverse('ws_urls:tipo_conducta'),
                "logs": "/archivos/logs/apis.txt",
            },
        },
        safe=False,
    )

@require_http_methods(["GET"])
def mapeo_general(request):
    geopos = GeoPosicion.objects.all().values_list("domicilio__individuo__id", flat=True).distinct()
    #Obtenemos individuos de interes
    individuos = {
        i.id: i 
        for i in Individuo.objects.filter(id__in=geopos).select_related('situacion_actual', 'domicilio_actual')
    }
    #Obtenemos ultimas posiciones gps
    last_geopos = {
        g.domicilio.individuo.id: g
        for g in GeoPosicion.objects.filter(domicilio__individuo__id__in=geopos).select_related('domicilio', 'domicilio__individuo')
    }
    #Generamos diccionario
    resultado = {}
    for id in geopos:
        individuo = individuos[id]#Traemos individuo del dict
        #Creamos item
        resultado[id] = {
            "estado": individuo.get_situacion().estado,
            "estado_desc": individuo.get_situacion().get_estado_display(),
            "conducta": individuo.get_situacion().conducta,
            "conducta_desc": individuo.get_situacion().get_conducta_display(),
            "domicilio": str(individuo.domicilio_actual),
            "ultima_pocion": 
            {
                "latitud": last_geopos[id].latitud,
                "longitud": last_geopos[id].longitud,
                "aclaracion": last_geopos[id].aclaracion,
            },
        }
    return JsonResponse(resultado, safe=False, )

@csrf_exempt
@require_http_methods(["GET"])
def tracking_individuo(request, individuo_id):
    individuo = Individuo.objects.select_related('situacion_actual', 'domicilio_actual')
    individuo = individuo.get(pk=individuo_id)
    geoposiciones = GeoPosicion.objects.filter(domicilio__individuo=individuo)
    geoposiciones = {
        str(g.fecha)[0:16] : {
            "latitud": g.latitud, 
            "longitud": g.longitud, 
            "aclaracion": g.aclaracion,
        } for g in geoposiciones
    }
    return JsonResponse(
        {
            "estado": individuo.get_situacion().estado,
            "estado_desc": individuo.get_situacion().get_estado_display(),
            "conducta": individuo.get_situacion().conducta,
            "conducta_desc": individuo.get_situacion().get_conducta_display(),
            "domicilio": str(individuo.domicilio_actual),
            "posiciones": geoposiciones,
        },
        safe=False,
    )
    
