#Imports de python
import logging
#Imports de Django
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
#Imports del proyecto
from informacion.models import Individuo
#Imports de la app
from .models import GeoPosicion
from .functions import obtener_trackeados, obtener_geoposiciones

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
                "estados": reverse('wservices:tipo_estado'),
                "conductas": reverse('wservices:tipo_conducta'),
                "logs": "/archivos/logs/apis.txt",
            },
        },
        safe=False,
    )

@require_http_methods(["GET"])
def mapeo_general(request):
    #Obtenemos geoposiciones
    geopos = GeoPosicion.objects.all()
    geopos = geopos.select_related('individuo')
    geopos = geopos.select_related('individuo__situacion_actual')
    geopos = geopos.select_related('individuo__domicilio_actual', 'individuo__domicilio_actual__localidad')
    geopos = geopos.order_by('fecha')
    #Obtenemos la ultima posicion de cada uno
    last_geopos = {}
    for g in geopos:
        last_geopos[g.individuo.pk] = g
    #Generamos respuesta:
    resultado = {}
    for pk in last_geopos:
        geopos = last_geopos[pk]
        individuo = geopos.individuo
        sit_actual = individuo.get_situacion()
        #Creamos item
        resultado[individuo.num_doc] = {
            "estado":sit_actual.estado,
            "estado_desc": sit_actual.get_estado_display(),
            "conducta": sit_actual.conducta,
            "conducta_desc": sit_actual.get_conducta_display(),
            "domicilio": str(individuo.domicilio_actual),
            "ultima_pocion": 
            {
                "tipo": geopos.get_tipo_display(),
                "latitud": geopos.latitud,
                "longitud": geopos.longitud,
                "aclaracion": geopos.aclaracion,
            },
        }
    return JsonResponse(resultado, safe=False, )

@csrf_exempt
@require_http_methods(["GET"])
def tracking_individuo(request, individuo_id):
    individuo = Individuo.objects.select_related('situacion_actual', 'domicilio_actual')
    individuo = individuo.prefetch_related('geoposiciones')
    individuo = individuo.get(pk=individuo_id)
    geoposiciones = obtener_geoposiciones(individuo)
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
    
