#Imports de python
import json
import logging
#Imports de Django
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
#Imports del proyecto
from georef.models import Nacionalidad, Localidad
#Imports de la app
from .models import Individuo, AppData, Domicilio, GeoPosicion
from .models import Atributo, Sintoma, Situacion, Seguimiento
#Definimos logger
logger = logging.getLogger('apis')

@csrf_exempt
@require_http_methods(["POST"])
def registro_covidapp(request):
    data = None
    #Registramos ingreso de info
    #Recibimos el json
    data = json.loads(request.body.decode("utf-8"))
    #Obtenemos datos basicos:
    nac = Nacionalidad.objects.filter(nombre__icontains="Argentina").first()
    #Agarramos el dni
    num_doc = str(data["dni"]).upper()
    #Buscamos al individuo en la db
    try:#Si lo encontramos, lo usamos
        individuo = Individuo.objects.get(num_doc=num_doc)
    #Si no existe lo creamos
    except Individuo.DoesNotExist:
        individuo = Individuo()
        individuo.individuo = individuo
        individuo.num_doc = num_doc
        individuo.apellidos = data["apellido"]
        individuo.nombres = data["nombre"]
        individuo.nacionalidad = nac
        individuo.observaciones = "AUTODIAGNOSTICO"
        individuo.save()
    #PROCESAMOS INFO DE APP
    if not hasattr(individuo,'appdata'):
        appdata = AppData()
        appdata.individuo = individuo
    else:
        appdata = individuo.appdata
    #Procesamos los datos que si nos importan
    if not hasattr(individuo, 'telefono'):
        individuo.telefono = str(data["telefono"])
        individuo.save()
    else:
        appdata.telefono = str(data["telefono"])
    appdata.save()
    #Cargamos un nuevo domicilio:
    Domicilio.objects.filter(individuo=individuo, aclaracion="AUTODIAGNOSTICO").delete()
    domicilio = Domicilio(individuo=individuo)
    domicilio.calle = data["direccion_calle"]
    domicilio.numero = str(data["direccion_numero"])
    domicilio.localidad = Localidad.objects.first()
    domicilio.aclaracion = "AUTODIAGNOSTICO"
    domicilio.save()
    #Respondemos que fue procesado
    return JsonResponse(
        {
            "action":"registro",
            "realizado": True,
        },
        safe=False
    )

@csrf_exempt
@require_http_methods(["POST"])
def encuesta_covidapp(request):
    data = None
    #Registramos ingreso de info
    logger.info('\nENCUESTA: '+str(timezone.now())[0:16])
    logger.info(request.body)
    #Recibimos el json
    data = json.loads(request.body.decode("utf-8"))
    #Agarramos el dni
    num_doc = str(data["dni"]).upper()
    #Buscamos al individuo en la db
    try:
        individuo = Individuo.objects.get(num_doc=num_doc)
    except Individuo.DoesNotExist:
        return JsonResponse(
        {
            "action":"encuesta",
            "realizado": False,
            "error": "No existe el Individuo",
        },
        safe=False,
        status=400,
    )
    #Cargamos datos importantes:
    #Atributos
    Atributo.objects.filter(individuo=individuo, aclaracion="ENCUESTAAPP").delete()
    if data["pais_riesgo"] or data["contacto_extranjero"]:
        atributo = Atributo(individuo=individuo)
        atributo.tipo = "CE"
        atributo.aclaracion = "ENCUESTAAPP"
        atributo.save()
    #Sintomas
    Sintoma.objects.filter(individuo=individuo, aclaracion="ENCUESTAAPP").delete()
    if data["fiebre"]:
        sintoma = Sintoma(individuo=individuo, tipo='FIE', aclaracion="ENCUESTAAPP")
        sintoma.save()
    if data["tos"]:
        sintoma = Sintoma(individuo=individuo, tipo='TOS', aclaracion="ENCUESTAAPP")
        sintoma.save()
    if data["dif_respirar"]:
        sintoma = Sintoma(individuo=individuo, tipo='DPR', aclaracion="ENCUESTAAPP")
        sintoma.save()
    #Resultado
    individuo.appdata.estado = [0,'R','A','V'][data["riesgo"]]
    individuo.appdata.save()
    #Cargamos nueva situacion
    if data["riesgo"] > 1:
        Situacion.objects.filter(individuo=individuo, aclaracion="AUTODIAGNOSTICO").delete()
        situacion = Situacion()
        situacion.individuo = individuo
        situacion.estado = 40
        situacion.conducta = 'C'
        situacion.aclaracion = "AUTODIAGNOSTICO"
        situacion.save()
    #Geoposicion
    if data["latitud"] and data["longitud"]:
        GeoPosicion.objects.filter(domicilio=individuo.domicilio_actual).delete()
        geopos = GeoPosicion()
        geopos.domicilio = individuo.domicilio_actual
        geopos.latitud = data["latitud"]
        geopos.longitud = data["longitud"]
        geopos.aclaracion = "AUTODIAGNOSTICO"
        geopos.save()
    logger.info('EXITO!')
    return JsonResponse(
        {
            "action":"encuesta",
            "realizado": True,
        },
        safe=False
    )

@csrf_exempt
@require_http_methods(["POST"])
def temperatura_covidapp(request):
    data = None
    #Recibimos el json
    data = json.loads(request.body.decode("utf-8"))
    #Agarramos el dni
    num_doc = str(data["dni"]).upper()
    #Buscamos al individuo en la db
    try:
        individuo = Individuo.objects.get(num_doc=num_doc)
    except Individuo.DoesNotExist:
        return JsonResponse(
        {
            "action":"temperatura",
            "realizado": False,
            "error": "No existe el Individuo",
        },
        safe=False,
        status=400,
    )
    #Cargamos datos importantes:
    seguimiento = Seguimiento()
    seguimiento.individuo = individuo
    seguimiento.tipo = 'A'
    seguimiento.aclaracion = "AUTODIAGNOSTICO - Temp:" + str(data["temperatura"])
    seguimiento.save()
    return JsonResponse(
        {
            "action":"temperatura",
            "realizado": True,
        },
        safe=False
    )