#Imports de python
import json
import logging
#Imports de Django
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
#Imports del proyecto
from georef.models import Nacionalidad, Localidad
#Imports de la app
from .models import Individuo, AppData, Domicilio, Situacion

@csrf_exempt
@require_http_methods(["POST"])
def registro_covidapp(request):
    #Sistema de loggin
    logger = logging.getLogger('apis')
    try:
        #Recibimos el json
        data = json.loads(request.body.decode("utf-8"))
        logger.info('registro_covidapp:'+str(data))
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
            individuo.apellidos = data["apellido"]
            individuo.nombres = data["nombre"]
            individuo.nacionalidad = nac
            individuo.aclaracion = "AUTODIAGNOSTICO"
            individuo.save()
        #Le creamos el estado Sospechoso-Evaluar (4-B)
        sit_actual = individuo.situacion_actual()
        if not sit_actual or (sit_actual and sit_actual.estado < 4):
            situacion = Situacion()
            situacion.individuo = individuo
            situacion.estado = 4
            situacion.conducta = 'B'
            situacion.aclaracion = "AUTODIAGNOSTICO"
            situacion.save()
        #PROCESAMOS INFO DE APP
        if not hasattr(individuo,'appdata'):
            appdata = AppData()
            appdata.individuo = individuo
        else:
            appdata = individuo.appdata
        #Procesamos los datos que si nos importan
        if not hasattr(individuo, 'telefono'):
            individuo.telefono = data["telefono"]
        else:
            appdata.telefono = data["telefono"]
        appdata.save()
        #Cargamos un nuevo domicilio:
        domicilio = Domicilio()
        domicilio.individuo = individuo
        domicilio.calle = data["direccion_calle"]
        domicilio.numero = data["direccion_numero"]
        #domicilio.localidad = data["localidad"]
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
    except Exception as e: 
        return JsonResponse(
            {
                "action":"registro",
                "realizado": False,
                "error": str(e),
            },
            status=400,
            safe=False
        )