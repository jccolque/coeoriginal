#Imports de python
import copy
import json
import logging
from base64 import b64decode
#Imports de Django
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
#Imports del proyecto
from operadores.models import Operador
from georef.models import Nacionalidad, Localidad
#Imports de la app
from .choices import TIPO_PERMISO
from .models import Individuo, AppData, Domicilio, GeoPosicion
from .models import Atributo, Sintoma, Situacion, Seguimiento
from .tokens import TokenGenerator
from .geofence import controlar_distancia

#Definimos logger
logger = logging.getLogger("apis")

@csrf_exempt
@require_http_methods(["GET"])
def AppConfig(request):
    return JsonResponse(
        {
            "action":"AppConfig",
            #WebServices
            "WebServices":
            {
                "localidad": reverse("georef:localidad-autocomplete"),
                "barrio": reverse("georef:barrio-autocomplete"),
                "logs": "/archivos/logs/apis.txt",
            },
            #Registro:
            "Registro":
            {
                "url": reverse("api_urls:registro"),
                "fields_request": 
                {
                    "dni": "str",
                    "apellido": "str",
                    "nombre": "str",
                    "localidad": "int: id_localidad",
                    "barrio": "int: id_barrio (opcional)",
                    "direccion_calle": "str",
                    "direccion_numero": "str",
                    "telefono": "str",
                    "email": "str (Opcional)",
                    "push_notification_id": "str",
                },
                "fields_response": 
                {
                    "action": "registro",
                    "realizado": "bool",
                    "token": "str: para validar envios posteriores",
                    "error": "str (Solo si hay errores)",
                },
            },
            "FotoPerfil":
            {
                "url": reverse("api_urls:foto_perfil"),
                "fields_request": 
                {
                    "dni": "str",
                    "token": "str: Obtenido en respuesta registro",
                    "imagen": "Base64",

                },
                "fields_response": 
                {
                    "action": "registro_avanzado",
                    "realizado": "bool",
                    "error": "str (Solo si hay errores)",
                }
            },
            #Encuesta
            "Encuesta":
            {
                "url": reverse("api_urls:encuesta"),
                "fields_request": 
                {
                    "dni": "str",
                    "token": "str: Obtenido en respuesta registro",
                    "pais_riesgo": "bool",
                    "contacto_extranjero": "bool",
                    "fiebre": "bool",
                    "tos": "bool",
                    "dif_respirar": "bool",
                    "riesgo": "int (1:Alto,2:Medio,3:Bajo)",
                    "latitud": "float", 
                    "longitud": "float",
                },
                "fields_response": 
                {
                    "action": "encuesta",
                    "realizado": "bool",
                    "error": "str (Solo si hay errores)",
                }
            },
            #Start Tracking
            "StartTracking":
            {
                "url": reverse("api_urls:start_tracking"),
                "fields": 
                {
                    "dni_individuo": "str",
                    "token": "str: Obtenido en respuesta registro",
                    "dni_operador": "str",
                    "password": "str",
                    "latitud": "float", 
                    "longitud": "float",
                },
                "fields_response": 
                {
                    "action": "start_tracking",
                    "realizado": "bool",
                    "error": "str (Solo si hay errores)",
                }
            },
            #Tracking
            "tracking": 
            {
                "url": reverse("api_urls:tracking"),
                "fields": 
                {
                    "dni_individuo": "str",
                    "token": "str: Obtenido en respuesta registro",
                    "fecha": "str: YYYYMMDD",
                    "hora": "str: HHMM",
                    "latitud": "float", 
                    "longitud": "float",
                },
                "fields_response": 
                {
                    "action": "tracking",
                    "realizado": "bool",
                    "distancia" : "float (en metros)",
                    "error": "str (Solo si hay errores)",
                },
                "parametros":
                {
                    'alerta_distancia': 50,
                    'alerta_mensaje': 'Alerta, usted se ha alejado por mas de 50 metros del punto fijado.',
                    'critico_distancia': 100,
                    'critico_mensaje': 'Usted se ha alejado mas de 100 metros del punto fijado, las fuerzas de seguridad estan siendo informadas.',
                },
            },
            #Salvoconducto Digital
            "salvoconducto":
            {
                "url": reverse("api_urls:salvoconducto"),
                "fields":
                {
                    "dni_individuo": "str",
                    "token": "str: Obtenido en respuesta registro",
                    "tipo_permiso": "str(1):id de TIPO_PERMISO",
                    "fecha_ideal": "str: YYYYMMDD",
                    "hora_ideal": "str: HHMM",
                },
                "fields_response": 
                {
                    "action": "salvoconducto",
                    "realizado": "bool",
                    "fecha": "datefield",
                    "hora_inicio": "timefield",
                    "hora_fin": "str: timefield",
                    "imagen": "url",
                    "qr": "url",
                    "texto": "str: leyenda de permiso autorizado",
                    "error": "str (Solo si hay errores/rechaza pedido)",
                },
                "parametros":
                {
                    'TIPO_PERMISO': TIPO_PERMISO,
                },
            },
        },
        safe=False,
    )

@csrf_exempt
@require_http_methods(["POST"])
def registro(request):
    try:
        data = None
        #Registramos ingreso de info
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        logger.info("registro:"+str(timezone.now())+"|"+str(data))
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
        if not hasattr(individuo,"appdata"):
            appdata = AppData()
            appdata.individuo = individuo
        else:
            appdata = individuo.appdata
        #Procesamos telefono si lo envio
        if not individuo.telefono == "+549388":
            individuo.telefono = str(data["telefono"])
            individuo.save()
        else:
            appdata.telefono = str(data["telefono"])
        #Procesamos email si lo envio
        if "email" in data:
            if not individuo.email:
                individuo.email = data["email"]
            else:
                appdata.email = data["email"]
        #Registramos push_not_id
        if "push_notification_id" in data:
            appdata.push_id = data["push_notification_id"]
        #Guardamos
        appdata.fecha = timezone.now()
        appdata.save()
        #Cargamos un nuevo domicilio:
        Domicilio.objects.filter(individuo=individuo, aclaracion="AUTODIAGNOSTICO").delete()
        domicilio = Domicilio(individuo=individuo)
        domicilio.calle = data["direccion_calle"]
        domicilio.numero = str(data["direccion_numero"])
        if "localidad" in data:
            domicilio.localidad = Localidad.objects.get(pk=data["localidad"])
        else:
            domicilio.localidad = Localidad.objects.first()
        domicilio.aclaracion = "AUTODIAGNOSTICO"
        domicilio.save()
        #Respondemos que fue procesado
        logger.info("Exito!")
        return JsonResponse(
            {
                "action":"registro",
                "realizado": True,
                "token": TokenGenerator(individuo),
            },
            safe=False
        )
    except Exception as e:
        logger.info("Falla: "+str(e))
        return JsonResponse(
            {
                "action":"registro",
                "realizado": False,
                "error": str(e),
            },
            safe=False,
            status=400,
        )

@csrf_exempt
@require_http_methods(["POST"])
def foto_perfil(request):
    try:
        data = None
        #Registramos ingreso de info
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        data2 = copy.copy(data)
        data2["imagen"] = data2["imagen"][:25]+'| full |'+data2["imagen"][-25:]
        logger.info("foto_perfil:"+str(timezone.now())+"|"+str(data2))
        #Agarramos el dni
        num_doc = str(data["dni"]).upper()
        #Buscamos al individuo en la db
        individuo = Individuo.objects.get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Cargamos la foto:
        image_data = b64decode(data['imagen'])
        individuo.fotografia = ContentFile(image_data, individuo.num_doc+'.jpg')
        individuo.save()
        #Terminamos proceso
        logger.info("Exito!")
        return JsonResponse(
            {
                "action":"foto_perfil",
                "realizado": True,
            },
            safe=False
        )
    except Exception as e:
        logger.info("Falla: "+str(e))
        return JsonResponse(
            {
                "action":"foto_perfil",
                "realizado": False,
                "error": str(e),
            },
            safe=False,
            status=400,
        )

@csrf_exempt
@require_http_methods(["POST"])
def encuesta(request):
    try:
        data = None
        #Registramos ingreso de info
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        logger.info("encuesta:"+str(timezone.now())+"|"+str(data))
        #Agarramos el dni
        num_doc = str(data["dni"]).upper()
        #Buscamos al individuo en la db
        individuo = Individuo.objects.get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

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
            sintoma = Sintoma(individuo=individuo, tipo="FIE", aclaracion="ENCUESTAAPP")
            sintoma.save()
        if data["tos"]:
            sintoma = Sintoma(individuo=individuo, tipo="TOS", aclaracion="ENCUESTAAPP")
            sintoma.save()
        if data["dif_respirar"]:
            sintoma = Sintoma(individuo=individuo, tipo="DPR", aclaracion="ENCUESTAAPP")
            sintoma.save()
        #Resultado
        individuo.appdata.estado = [0,"R","A","V"][data["riesgo"]]
        individuo.appdata.save()
        #Cargamos nueva situacion
        if data["riesgo"] > 1:
            Situacion.objects.filter(individuo=individuo, aclaracion="AUTODIAGNOSTICO").delete()
            situacion = Situacion()
            situacion.individuo = individuo
            situacion.estado = 40
            situacion.conducta = "C"
            situacion.aclaracion = "AUTODIAGNOSTICO"
            situacion.save()
        #Geoposicion
        if data["latitud"] and data["longitud"]:
            geopos = GeoPosicion()
            geopos.domicilio = individuo.domicilio_actual
            geopos.latitud = data["latitud"]
            geopos.longitud = data["longitud"]
            geopos.aclaracion = "AUTODIAGNOSTICO"
            geopos.save()
        logger.info("Exito!")
        return JsonResponse(
            {
                "action":"encuesta",
                "realizado": True,
            },
            safe=False
        )
    except Exception as e:
        logger.info("Falla: "+str(e))
        return JsonResponse(
            {
                "action":"encuesta",
                "realizado": False,
                "error": str(e),
            },
            safe=False,
            status=400,
        )

@csrf_exempt
@require_http_methods(["POST"])
def temperatura(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        logger.info("temperatura:"+str(timezone.now())+"|"+str(data))
        #Agarramos el dni
        num_doc = str(data["dni"]).upper()
        #Buscamos al individuo en la db
        individuo = Individuo.objects.get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Cargamos datos importantes:
        seguimiento = Seguimiento()
        seguimiento.individuo = individuo
        seguimiento.tipo = "A"
        seguimiento.aclaracion = "AUTODIAGNOSTICO - Temp:" + str(data["temperatura"])
        seguimiento.save()
        logger.info("Exito!")
        return JsonResponse(
            {
                "action":"temperatura",
                "realizado": True,
            },
            safe=False
        )
    except Exception as e:
        logger.info("Falla: "+str(e))
        return JsonResponse(
            {
                "action":"temperatura",
                "realizado": False,
                "error": str(e),
            },
            safe=False,
            status=400,
        )

@csrf_exempt
@require_http_methods(["POST"])
def start_tracking(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        data2 = copy.copy(data)
        data2["password"] = "OCULTA"
        logger.info("start_tracking:"+str(timezone.now())+"|"+str(data2))
        #Agarramos el dni
        num_doc = str(data["dni_individuo"]).upper()
        #Buscamos al individuo en la db
        individuo = Individuo.objects.get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Chequeamos credenciales de operador
        operador = Operador.objects.get(num_doc=data["dni_operador"])
        user = authenticate(username=operador.usuario, password=data["password"])
        if not user:
            return JsonResponse(
            {
                "action":"start_tracking",
                "realizado": False,
                "error": "El operador no existe.",
            },
            safe=False,
            status=400,
        )
        #Guardamos la geoposicion BASE
        GeoPosicion.objects.filter(domicilio__individuo=individuo, aclaracion__icontains="INICIO TRACKING").delete()
        GeoPosicion.objects.filter(domicilio__individuo=individuo, aclaracion="TRACKING").delete()
        geopos = GeoPosicion()
        geopos.domicilio = individuo.domicilio_actual
        geopos.latitud = data["latitud"]
        geopos.longitud = data["longitud"]
        geopos.aclaracion = "INICIO TRACKING: " + str(geopos.latitud)+", "+str(geopos.longitud)
        geopos.save()
        #Cargamos Inicio de Seguimiento:
        Seguimiento.objects.filter(tipo__in=("IT","AT", "FT")).delete()
        seguimiento = Seguimiento()
        seguimiento.individuo = individuo
        seguimiento.tipo = "IT"
        seguimiento.aclaracion = "INICIO TRACKING: " + str(geopos.latitud)+", "+str(geopos.longitud)
        seguimiento.save()
        #Respondemos
        logger.info("Exito!")
        return JsonResponse(
            {
                "action":"start_tracking",
                "realizado": True,
            },
            safe=False
        )
    except Exception as e:
        logger.info("Falla: "+str(e))
        return JsonResponse(
            {
                "action":"start_tracking",
                "realizado": False,
                "error": str(e),
            },
            safe=False,
            status=400,
        )

@csrf_exempt
@require_http_methods(["POST"])
def tracking(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        logger.info("tracking:"+str(timezone.now())+"|"+str(data))
        #Agarramos el dni
        num_doc = str(data["dni"]).upper()
        #Buscamos al individuo en la db
        individuo = Individuo.objects.get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Guardamos nueva posgps
        geopos = GeoPosicion()
        geopos.domicilio = individuo.domicilio_actual
        geopos.latitud = data["latitud"]
        geopos.longitud = data["longitud"]
        geopos.aclaracion = "TRACKING"
        geopos.fecha = timezone.datetime(
            int(data["fecha"][0:4]),
            int(data["fecha"][4:6]),
            int(data["fecha"][6:8]),
            int(data["hora"][0:2]),
            int(data["hora"][2:4]),
        )
        geopos.save()
        #Controlamos posicion:
        distancia = controlar_distancia(geopos)
        logger.info("Exito")
        return JsonResponse(
            {
                "action":"tracking",
                "realizado": True,
                "distancia": distancia,
            },
            safe=False
        )
    except Exception as e:
        logger.info("Falla: "+str(e))
        return JsonResponse(
            {
                "action":"tracking",
                "realizado": False,
                "error": str(e),
            },
            safe=False,
            status=400,
        )

@csrf_exempt
@require_http_methods(["POST"])
def salvoconducto(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        logger.info("salvoconducto:"+str(timezone.now())+"|"+str(data))
        #Agarramos el dni
        num_doc = str(data["dni"]).upper()
        #Buscamos al individuo en la db
        individuo = Individuo.objects.select_related('appdata').get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Obtenemos datos del pedido de permiso:
        permiso = data["tipo_permiso"]
        fecha = timezone.datetime(
            int(data["fecha_ideal"][0:4]),
            int(data["fecha_ideal"][4:6]),
            int(data["fecha_ideal"][6:8]),
            int(data["hora_ideal"][0:2]),
            int(data["hora_ideal"][2:4]),
        )
        #Validamos si es factible:
            #REALIZAR TODA LA LOGICA
            #POR AHORA RESPONDE PERMISO
        #Si todo salio bien
        logger.info("Exito")
        return JsonResponse(
            {
                "action": "salvoconducto",
                "realizado": True,
                "fecha": str(timezone.now().date()),
                "hora_inicio": str(timezone.now().time()),
                "hora_fin": str(timezone.now().time()),
                "imagen": individuo.get_foto(),
                "qr": individuo.get_qr(),
                "texto": "Aprobado sin validacion, para test.",

            },
            safe=False
        )
    except Exception as e:
        logger.info("Falla: "+str(e))
        return JsonResponse(
            {
                "action":"salvoconducto",
                "realizado": False,
                "error": str(e),
            },
            safe=False,
            status=400,
        )        