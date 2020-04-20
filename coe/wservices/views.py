#Imports PYthon
import json
#Imports Django
from django.apps import apps
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
#Imports del proyecto
from core.decoradores import superuser_required
from georef.models import Localidad, Barrio
from informacion.choices import TIPO_ESTADO, TIPO_CONDUCTA
from informacion.models import Situacion
from permisos.choices import TIPO_PERMISO

# Create your views here.
@staff_member_required
def menu(request):
    return render(request, 'menu_wservices.html', {})

#Web Servis generico para todas las apps del sistema
#Si el modelo tiene as_dict, aparece.
@superuser_required
def ws(request, nombre_app=None, nombre_modelo=None):
    if nombre_app and nombre_modelo:
        if apps.all_models[nombre_app][nombre_modelo.lower()]:
            modelo = apps.all_models[nombre_app][nombre_modelo.lower()]
            if hasattr(modelo, 'as_dict'):
                datos = modelo.objects.all()
                datos = [d.as_dict() for d in datos]
                return HttpResponse(json.dumps({nombre_modelo+'s': datos, "cant_registros": len(datos),}), content_type='application/json')

    apps_listas = {}
    for app, models in apps.all_models.items():
        for model in models.values():
            if hasattr(model, 'as_dict'):
                if app in apps_listas:
                    apps_listas[app].append(model._meta.model_name)
                else:
                    apps_listas[app] = [model._meta.model_name, ]
    return render(request, 'ws.html', {"apps_listas": apps_listas,})

#Creamos nuestros webservices
@require_http_methods(["GET"])
def ws_situaciones(request, fecha=None):
    #Agregar por localidad
    estados = {}
    conductas = {}
    #Traemos todas las situaciones
    situaciones = Situacion.objects.all()
    #Si filtra por fecha
    if fecha:#Filtramos \_o_/
        situaciones = situaciones.objects.get(fecha__date=fecha)
    #Genermaos listado por conductas
    for s in situaciones:
        #Contamos estados
        if s.get_estado_display() in estados:
            estados[s.get_estado_display()] += 1
        else:
            estados[s.get_estado_display()] = 1
        #Contamos conductas
        if s.get_conducta_display() in conductas:
            conductas[s.get_conducta_display()] += 1
        else:
            conductas[s.get_conducta_display()] = 1
    #Le cambiamos los valores:
    return JsonResponse(
        {
            "action": "situaciones",
            "fecha": timezone.now(),
            "estados": estados,
            "conductas": conductas,
        },
        safe=False
    )

@require_http_methods(["GET"])
def tipo_estado(request):
    return JsonResponse(
        {
            "permisos": [{"id":tipo[0],"descripcion":tipo[1]} for tipo in TIPO_ESTADO],
        },
        safe=False,
    )

@require_http_methods(["GET"])
def tipo_conducta(request):
    return JsonResponse(
        {
            "permisos": [{"id":tipo[0],"descripcion":tipo[1]} for tipo in TIPO_CONDUCTA],
        },
        safe=False,
    )


@require_http_methods(["GET"])
def tipo_permiso(request):
    return JsonResponse(
        {
            "permisos": [{"id":tipo[0],"descripcion":tipo[1]} for tipo in TIPO_PERMISO if tipo[0] != 'P'],
        },
        safe=False,
    )

@require_http_methods(["GET"])
def ws_localidades(request):
    datos = Localidad.objects.all()
    datos = [d.as_dict() for d in datos]
    return HttpResponse(json.dumps({'Localidades': datos, "cant_registros": len(datos),}), content_type='application/json')
    
@require_http_methods(["GET"])
def ws_barrios(request, localidad_id=None):
    datos = Barrio.objects.all()
    if localidad_id:
        datos = datos.filter(localidad__id=localidad_id)
    datos = [d.as_dict() for d in datos]
    return HttpResponse(json.dumps(
        {
            'localidad_id': localidad_id,
            'barrios': datos,
            "cant_registros": len(datos),
        }), content_type='application/json')