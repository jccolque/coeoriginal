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
from .geofence import obtener_trackeados

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
    #geopos = GeoPosicion.objects.all().values_list("individuo__id", flat=True).distinct()
    #Obtenemos individuos de interes
    #individuos = {
    #    i.id: i 
    #    for i in Individuo.objects.filter(id__in=geopos).select_related('situacion_actual', 'domicilio_actual')
    #}
    #Obtenemos ultimas posiciones gps
    #last_geopos = {
    #    g.individuo.id: g
    #    for g in GeoPosicion.objects.filter(individuo__id__in=geopos).select_related('individuo')
    #}
    #Generamos diccionario
    #resultado = {}
    # for id in geopos:
    #     individuo = individuos[id]#Traemos individuo del dict
    #     #Creamos item
    #     resultado[id] = {
    #         "estado": individuo.get_situacion().estado,
    #         "estado_desc": individuo.get_situacion().get_estado_display(),
    #         "conducta": individuo.get_situacion().conducta,
    #         "conducta_desc": individuo.get_situacion().get_conducta_display(),
    #         "domicilio": str(individuo.domicilio_actual),
    #         "ultima_pocion": 
    #         {
    #             "latitud": last_geopos[id].latitud,
    #             "longitud": last_geopos[id].longitud,
    #             "aclaracion": last_geopos[id].aclaracion,
    #         },
    #     }
    # return JsonResponse(resultado, safe=False, )
    return ''

@csrf_exempt
@require_http_methods(["GET"])
def tracking_individuo(request, individuo_id):
    individuo = Individuo.objects.select_related('situacion_actual', 'domicilio_actual')
    individuo = individuo.prefetch_related('geoposiciones')
    individuo = individuo.get(pk=individuo_id)
    geoposiciones = GeoPosicion.objects.filter(individuo=individuo)
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
    
