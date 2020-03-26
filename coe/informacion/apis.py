#Imports de python
import json
#Imports de Django
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
#Imports del proyecto
from georef.models import Nacionalidad, Localidad
#Imports de la app
from .models import Individuo, AppData, Domicilio

@csrf_exempt
@require_http_methods(["POST"])
def registro_covidapp(request):
    try:
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
            individuo.apellidos = data["apellido"]
            individuo.nombres = data["nombre"]
            individuo.nacionalidad = nac
            individuo.save()
        #PROCESAMOS INFO DE APP
        if not hasattr(individuo,'appdata'):
            appdata = AppData()
            appdata.individuo = individuo
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
        domicilio.aclaracion = "CARGADO DESDE APP"
        domicilio.save()
        #Respondemos que fue procesado
        return JsonResponse(
            {
                "action":"registro",
                "realizado": True,
            },safe=False)
    except Exception as e: 
        return JsonResponse(
            {
                "action":"registro",
                "realizado": False,
                "error": str(e),
            },safe=False)