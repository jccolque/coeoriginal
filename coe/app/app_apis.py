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
#Imports Extras
from fcm_django.models import FCMDevice
#Imports del proyecto
from core.functions import json_error
from operadores.models import Operador
from georef.functions import obtener_argentina
from georef.models import Localidad
from informacion.models import Individuo, Domicilio
from informacion.models import Atributo, Sintoma, Situacion
from seguimiento.models import Seguimiento
from geotracking.models import GeoPosicion
from geotracking.geofence import controlar_distancia, control_movimiento, es_local
from permisos.functions import horario_activo
from permisos.functions import buscar_permiso, validar_permiso, json_permiso
from permisos.choices import TIPO_PERMISO
from denuncias.models import DenunciaAnonima
#Imports de la app
from .models import AppData
from .tokens import TokenGenerator
from .functions import obtener_dni

#Definimos logger
logger = logging.getLogger("apis")

@csrf_exempt
@require_http_methods(["GET"])
def AppConfig(request):
    return JsonResponse(
        {
            "accion":"AppConfig",
            #WebServices
            "WebServices":
            {
                "tipo_permisos": reverse("wservices:tipo_permiso"),
                "full_localidades": reverse("wservices:ws_localidades"),
                "full_barrios": reverse("wservices:ws_barrios"),
                "ac_localidad": reverse("georef:localidad-autocomplete"),
                "ac_barrio": reverse("georef:barrio-autocomplete"),
                "logs": "/archivos/logs/apis.txt",
            },
            #Registro:
            "Registro":
            {
                "url": reverse("app:registro"),
                "fields_request": 
                {
                    "dni_individuo": "str",
                    "apellido": "str",
                    "nombre": "str",
                    "localidad": "int: id_localidad",
                    "localidad_nombre": "str: nombre completo desde ws",
                    "barrio": "int: id_barrio (opcional)",
                    "direccion_calle": "str",
                    "direccion_numero": "str",
                    "telefono": "str",
                    "email": "str (Opcional)",
                    "push_notification_id": "str",
                },
                "fields_response": 
                {
                    "accion": "registro",
                    "realizado": "bool",
                    "token": "str: para validar envios posteriores",
                    "error": "str (Solo si hay errores)",
                },
            },
            "FotoPerfil":
            {
                "url": reverse("app:foto_perfil"),
                "fields_request": 
                {
                    "dni_individuo": "str",
                    "token": "str: Obtenido en respuesta registro",
                    "imagen": "Base64",

                },
                "fields_response": 
                {
                    "accion": "registro_avanzado",
                    "realizado": "bool",
                    "error": "str (Solo si hay errores)",
                }
            },
            #Encuesta
            "Encuesta":
            {
                "url": reverse("app:encuesta"),
                "fields_request": 
                {
                    "dni_individuo": "str",
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
                    "accion": "encuesta",
                    "realizado": "bool",
                    "error": "str (Solo si hay errores)",
                }
            },
            #Start Tracking
            "StartTracking":
            {
                "url": reverse("app:start_tracking"),
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
                    "accion": "start_tracking",
                    "realizado": "bool",
                    "error": "str (Solo si hay errores)",
                }
            },
            #Tracking
            "tracking": 
            {
                "url": reverse("app:tracking"),
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
                    "accion": "tracking",
                    "realizado": "bool",
                    "alerta": "str: Tipo de Alerta",
                    "notif_titulo": "str (Titulo notificacion Local)",
                    "notif_mensaje": "str (Mensaje notificacion Local)",
                    "distancia" : "float (en metros)",
                    "prox_tracking": "int (Minutos hasta proximo envio)",
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
            #Obtener Salvoconducto Digital
            "ver_salvoconducto":
            {
                "url": reverse("app:ver_salvoconducto"),
                "fields":
                {
                    "dni_individuo": "str",
                    "token": "str: Obtenido en respuesta registro",            
                },
                "fields_response": 
                {
                    "accion": "salvoconducto",
                    "realizado": "bool",
                    "tipo_permiso": "str: Descripcion del permiso",
                    "dni_individuo": "str",
                    "nombre_completo": "str",
                    "domicilio": "str",
                    "fecha_inicio": "datefield",
                    "hora_inicio": "timefield",
                    "fecha_fin": "datefield",
                    "hora_fin": "str: timefield",
                    "imagen": "url",
                    "qr": "url",
                    "texto": "str: leyenda de permiso autorizado",
                    "control": "bool: Si puede controlar otros permisos",
                    "error": "str (Solo si hay errores/rechaza pedido)",
                },
            },
            #Salvoconducto Digital
            "pedir_salvoconducto":
            {
                "url": reverse("app:pedir_salvoconducto"),
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
                    "accion": "salvoconducto",
                    "realizado": "bool",
                    "tipo_permiso": "str: Descripcion del permiso",
                    "dni_individuo": "str",
                    "nombre_completo": "str",
                    "domicilio": "str",
                    "fecha_inicio": "datefield",
                    "hora_inicio": "timefield",
                    "fecha_fin": "datefield",
                    "hora_fin": "str: timefield",
                    "imagen": "url",
                    "qr": "url",
                    "texto": "str: leyenda de permiso autorizado",
                    "control": "bool: Si puede controlar otros permisos",
                    "error": "str (Solo si hay errores/rechaza pedido)",
                },
                "parametros":
                {
                    'TIPO_PERMISO': {tp[0]:tp[1] for tp in TIPO_PERMISO if tp[0] != 'P'},
                },
            },
            #Control de SalvoConducto
            "control_salvoconducto":
            {
                "url": reverse("app:control_salvoconducto"),
                "fields":
                {
                    "dni_operador": "str (Del Dueño del celular)",
                    "qr_code": "El QR que se leyo",
                    "latitud": "float", 
                    "longitud": "float",
                },
                "fields_response": 
                {
                    "accion": "control_salvoconducto",
                    "realizado": "bool",
                    "tipo_permiso": "str: Descripcion del permiso",
                    "dni_individuo": "str",
                    "nombre_completo": "str",
                    "domicilio": "str",
                    "fecha_inicio": "datefield",
                    "hora_inicio": "timefield",
                    "fecha_fin": "datefield",
                    "hora_fin": "str: timefield",
                    "imagen": "url",
                    "qr": "url",
                    "texto": "str: leyenda de permiso autorizado",
                    "control": "bool: Si puede controlar otros permisos",
                    "error": "str (Solo si hay errores/rechaza pedido)",
                },
            },
            #Notifaciones
            "Notificaciones":
            {
                "url": reverse("app:notificacion"),
                "fields":
                {
                    "dni_individuo": "str",
                    "token": "str: Obtenido en respuesta registro",
                },
            "fields_response": 
                {
                    "accion": "notificacion",
                    "realizado": "bool",
                    "notif_titulo": "str (Titulo notificacion Local | si realizado=True)",
                    "notif_mensaje": "str (Mensaje notificacion Local | si realizado=True)",
                    "error": "str (Solo si hay errores)",
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
        logger.info("Intento Registro: " + str(data))
        #Agarramos el dni
        num_doc = obtener_dni(data)
        #Buscamos al individuo en la db
        try:#Si lo encontramos, lo usamos
            individuo = Individuo.objects.get(num_doc=num_doc)
        #Si no existe lo creamos
        except Individuo.DoesNotExist:
            individuo = Individuo()
            individuo.individuo = individuo
            individuo.num_doc = num_doc
            individuo.apellidos = " ".join([word.capitalize() for word in data["apellido"].split(" ")])
            individuo.nombres = " ".join([word.capitalize() for word in data["nombre"].split(" ")])
            individuo.nacionalidad = obtener_argentina()
            individuo.observaciones = "AUTODIAGNOSTICO"
            individuo.save()
        #PROCESAMOS INFO DE APP
        if not hasattr(individuo,"appdata"):
            appdata = AppData()
            appdata.individuo = individuo
        else:
            appdata = individuo.appdata
        #Procesamos telefono si lo envio
        if individuo.telefono == "+549388":
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
            FCMDevice.objects.filter(name=individuo.num_doc).delete()
            device = FCMDevice()
            device.name = individuo.num_doc
            device.registration_id = data["push_notification_id"]
            device.type = 'android'
            if "device_id" in data:
                device.device_id = data["device_id"]
            device.save()
            #Le registramos su dispositivo
            individuo.device = device
            individuo.save()
        #Guardamos
        appdata.fecha = timezone.now()
        appdata.save()
        #Cargamos un nuevo domicilio:
        domicilio = Domicilio(individuo=individuo)
        domicilio.calle = data["direccion_calle"]
        domicilio.numero = str(data["direccion_numero"])
        if "localidad" in data:
            domicilio.localidad = Localidad.objects.get(pk=data["localidad"])
        elif "localidad_nombre" in data:
            localidad, departamento = data["localidad_nombre"].split('(')
            localidad = localidad[:-1]
            departamento = departamento[:-1]
            domicilio.localidad = Localidad.objects.get(nombre=localidad, departamento__nombre=departamento)
        else:
            domicilio.localidad = Localidad.objects.first()
        domicilio.aclaracion = "AUTODIAGNOSTICO"
        #Si esta en aislamiento no queremos sacarlo, bulkcreamos.
        if individuo.domicilio_actual:
            Domicilio.objects.bulk_create([domicilio, ])
        else:
            domicilio.save()
        #Respondemos que fue procesado
        return JsonResponse(
            {
                "accion":"registro",
                "realizado": True,
                "token": TokenGenerator(individuo),
            },
            safe=False
        )
    except Exception as e:
        return json_error(e, "registro", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def foto_perfil(request):
    try:
        data = None
        #Agarramos el dni
        try:
            num_doc = obtener_dni(data)
            #Si viene en un json
            data = json.loads(request.body.decode("utf-8"))
            #Codificamos imagen
            image_data = b64decode(data['imagen'])
            data["imagen"] = data["imagen"][:25]+'| full |'+data["imagen"][-25:]
        except:#Si viene por form
            num_doc = str(request.POST['dni']).upper()
            image_data = request.FILES['imagen'].read()
        #Buscamos al individuo en la db
        individuo = Individuo.objects.get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Cargamos la foto:
        individuo.fotografia = ContentFile(image_data, individuo.num_doc+'.jpg')
        individuo.save()
        #Terminamos proceso
        return JsonResponse(
            {
                "accion":"foto_perfil",
                "realizado": True,
            },
            safe=False
        )
    except Exception as e:
        return json_error(e, "foto_perfil", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def encuesta(request):
    try:
        data = None
        #Registramos ingreso de info
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        #Agarramos el dni
        num_doc = obtener_dni(data)
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
        situacion = Situacion()
        situacion.individuo = individuo
        if data["riesgo"] > 3:
            situacion.estado = 40
            situacion.conducta = 'B'
        #Guardamos si o si
        situacion.aclaracion = "AUTODIAGNOSTICO"
        if not individuo.situacion_actual:
            situacion.save()
        else:
            Situacion.objects.bulk_create([situacion, ])
        #Geoposicion
        if float(data["latitud"]) and float(data["longitud"]):
            geopos = GeoPosicion()
            geopos.individuo = individuo
            geopos.tipo = 'AD'
            geopos.latitud = float(data["latitud"])
            geopos.longitud = float(data["longitud"])
            geopos.aclaracion = "AUTODIAGNOSTICO"
            if es_local(geopos):
                geopos.save()
        return JsonResponse(
            {
                "accion": "encuesta",
                "realizado": True,
            },
            safe=False
        )
    except Exception as e:
        return json_error(e, "encuesta", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def start_tracking(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        #Agarramos el dni
        num_doc = obtener_dni(data)
        #Buscamos al individuo en la db
        individuo = Individuo.objects.get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Chequeamos credenciales de operador
        operador = Operador.objects.get(num_doc=data["dni_operador"])
        user = authenticate(username=operador.usuario, password=data["password"])
        if not user:
            data["password"] = "OCULTA"
            e = "No se pudo validar Operador"
            return json_error(e, "start_tracking", logger, data)
        #Guardamos la geoposicion BASE (Eliminamos todas las anteriores)
        if float(data["latitud"]) == 0:
            return JsonResponse(
            {
                "accion":"start_tracking",
                "realizado": False,
                "error": "Su GPS esta reportando coordenadas incorrectas.",
            },
            safe=False,
            status=400,
        )
        GeoPosicion.objects.filter(individuo=individuo, tipo__in=('ST', 'TC')).delete()
        geopos = GeoPosicion()
        geopos.individuo = individuo
        geopos.tipo = 'ST'
        geopos.latitud = float(data["latitud"])
        geopos.longitud = float(data["longitud"])
        geopos.aclaracion = "Iniciado por: " + str(operador)
        geopos.operador = operador
        if es_local(geopos):
            geopos.save()
            #Cargamos Inicio de Seguimiento:
            Seguimiento.objects.filter(tipo__in=("IT","AT", "FT")).delete()
            seguimiento = Seguimiento()
            seguimiento.individuo = individuo
            seguimiento.tipo = "IT"
            seguimiento.aclaracion = "Iniciado por: " + str(operador)
            seguimiento.save()
            #Respondemos
            return JsonResponse(
                {
                    "accion":"start_tracking",
                    "realizado": True,
                    "guardado": geopos.pk,
                },
                safe=False
            )
        else:
            #Respondemos
            return JsonResponse(
                {
                    "accion":"start_tracking",
                    "realizado": False,
                    "error": "Coordenadas fuera de la provincia.",
                },
                safe=False
            )
    except Exception as e:
        data["password"] = "OCULTA"
        return json_error(e, "start_tracking", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def tracking(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        #Agarramos el dni
        num_doc = obtener_dni(data)
        #Buscamos al individuo en la db
        individuo = Individuo.objects.select_related('appdata').get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Guardamos nueva posgps
        geopos = GeoPosicion()
        geopos.individuo = individuo
        geopos.tipo = 'RG'
        geopos.latitud = float(data["latitud"])
        geopos.longitud = float(data["longitud"])
        geopos.aclaracion = "TRACKING"
        geopos.fecha = timezone.datetime(
            int(data["fecha"][0:4]),
            int(data["fecha"][4:6]),
            int(data["fecha"][6:8]),
            int(data["hora"][0:2]),
            int(data["hora"][2:4]),
        )
        #Realizamos controles
        if horario_activo():#Si no es hora de dormir
            geopos = control_movimiento(geopos)
        #Que no se aleje de lo permitido
        geopos = controlar_distancia(geopos)
        #Guardamos siempre por ahora:
        geopos.save()
        #Controlamos posicion:
        return JsonResponse(
            {
                "accion":"tracking",
                "realizado": True,
                "prox_tracking": individuo.appdata.intervalo,#Minutos
                "distancia": int(geopos.distancia),
                "alerta": (geopos.alerta != 'SA'),
                "notif_titulo": geopos.get_alerta_display(),
                "notif_mensaje": geopos.notif_mensaje,
            },
            safe=False
        )
    except Exception as e:
        return json_error(e, "tracking", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def pedir_salvoconducto(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        #Agarramos el dni
        num_doc = obtener_dni(data)
        #Buscamos al individuo en la db
        individuo = Individuo.objects.select_related('appdata', 'domicilio_actual', 'situacion_actual')
        individuo = Individuo.objects.prefetch_related('permisos')
        individuo = individuo.get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN
        
        #Trabajamos
        #Obtenemos datos del pedido de permiso:
        fecha_ideal = timezone.datetime(
            int(data["fecha_ideal"][0:4]),
            int(data["fecha_ideal"][4:6]),
            int(data["fecha_ideal"][6:8]),
            int(data["hora_ideal"][0:2]),
            int(data["hora_ideal"][2:4]),
        )
        #Validamos si es factible:
        permiso = buscar_permiso(individuo)
        if not permiso.pk:#Si no hay un permiso guardado:
            permiso.tipo = data["tipo_permiso"]
            permiso.begda = fecha_ideal
            permiso = validar_permiso(individuo, permiso)
        #Si fue aprobado, Creamos Permiso
        if permiso.aprobar:#Variable temporal
            permiso.save()
            #Si todo salio bien
            return json_permiso(permiso, "salvoconducto")
        else:
            #Si se le niega por algun motivo
            logger.info("Denegado: " + permiso.aclaracion)
            return JsonResponse(
                {
                    "accion": "salvoconducto",
                    "realizado": permiso.aprobar,
                    "error": permiso.aclaracion,
                },
                safe=False,
                status=400,
            )
    except Exception as e:
        return json_error(e, "salvoconducto", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def ver_salvoconducto(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        #Agarramos el dni
        num_doc = obtener_dni(data)
        #Buscamos al individuo en la db
        individuo = Individuo.objects.select_related('appdata').get(num_doc=num_doc)
        #ACA CHEQUEAMOS TOKEN

        #Buscamos permiso
        permiso = buscar_permiso(individuo)
        #Damos respuesta
        return json_permiso(permiso, "ver_salvoconducto")
    except Exception as e:
        return json_error(e, "ver_salvoconducto", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def control_salvoconducto(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        #Agarramos el dni
        num_doc = str(data["dni_operador"]).upper()
        #Obtenemos el operador
        operador = Operador.objects.get(num_doc=num_doc)
        #Leemos QR y parceamos
        if "qr_code" in data:
            qr_code = data["qr_code"]
            if "@" in qr_code:#Es un DNI
                dni_qr = qr_code.split('@')[4]
                #Podriamos procesar el resto de la info del tipo
                #Fecha de Nacimiento
            elif "-" in qr_code:#Es permiso de App
                dni_qr = qr_code.split('-')[1]
        elif "dni_controlado" in data:
            dni_qr = data["dni_controlado"]
        #Buscamos al individuo en la db
        individuo = Individuo.objects.select_related('appdata').get(num_doc=dni_qr)
        #ACA CHEQUEAMOS TOKEN
        
        #Guardamos registro de control
        geopos = GeoPosicion()
        geopos.individuo = individuo
        geopos.tipo = "CG"
        geopos.latitud = float(data["latitud"])
        geopos.longitud = float(data["longitud"])
        geopos.aclaracion = "Control de Salvoconducto"
        geopos.operador = operador
        geopos.save()
        #Buscamos permiso
        permiso = buscar_permiso(individuo, activo=True)
        #Damos respuesta
        return json_permiso(permiso, "control_salvoconducto")
    except Exception as e:
        try:#Si logramos generar GeoPos del Control > Marcamos al infractor
            geopos.alerta = 'FP'#La marcamos como alerta
            geopos.save()
        except:
            pass
        e = 'El individuo no cuenta con un permiso activo.'
        return json_error(e, "control_salvoconducto", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def denuncia_anonima(request):
    try:
        data = None
        logger.info("Denuncia Anonima: " + str(request.POST))
        #Obtenemos los datos y guardamos
        denuncia = DenunciaAnonima()
        denuncia.tipo = request.POST['tipo_denuncia']
        denuncia.descripcion = request.POST['descripcion']
        denuncia.latitud = float(request.POST['latitud'])
        denuncia.longitud = float(request.POST['longitud'])
        #Capturamos la imagen
        image_data = request.FILES['imagen'].read()
        imagen_nombre = denuncia.tipo + '-' + str(timezone.now().timestamp()) + '.jpg'
        denuncia.imagen = ContentFile(image_data, imagen_nombre)
        #Guardamos
        denuncia.save()
        #Terminamos proceso
        return JsonResponse(
            {
                "accion":"denuncia_anonima",
                "realizado": True,
            },
            safe=False
        )
    except Exception as e:
        return json_error(e, "denuncia_anonima", logger, data)

@csrf_exempt
@require_http_methods(["POST"])
def notificacion(request):
    try:
        data = None
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        #Agarramos el dni
        num_doc = obtener_dni(data)
        #Buscamos al individuo en la db
        individuo = Individuo.objects.select_related('appdata', 'appdata__notificacion').get(num_doc=num_doc)
        notif = copy.copy(individuo.appdata.notificacion)
        individuo.appdata.notificacion.delete()
        #Damos respuesta
        return JsonResponse(
            {
                "accion": "notificacion",
                "realizado": True,
                "message":
                {
                    "title": notif.titulo,
                    "body": notif.mensaje,
                },
                "action": notif.get_accion_display(),

            },
            safe=False
        )
    except Exception as e:
        return json_error(e, "notificacion", logger, data)