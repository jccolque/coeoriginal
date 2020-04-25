#Imports PYthon
import json
#Imports Django
from django.apps import apps
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from georef.models import Localidad, Barrio
from informacion.choices import TIPO_ESTADO, TIPO_CONDUCTA
from informacion.models import Individuo, Situacion
from permisos.choices import TIPO_PERMISO
from denuncias.choices import TIPO_DENUNCIA

#Publicos
#Creamos nuestros webservices
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

def tipo_estado(request):
    return JsonResponse(
        {
            "permisos": [{"id":tipo[0],"descripcion":tipo[1]} for tipo in TIPO_ESTADO],
        },
        safe=False,
    )

def tipo_conducta(request):
    return JsonResponse(
        {
            "permisos": [{"id":tipo[0],"descripcion":tipo[1]} for tipo in TIPO_CONDUCTA],
        },
        safe=False,
    )

def tipo_permiso(request):
    return JsonResponse(
        {
            "permisos": [{"id":tipo[0],"descripcion":tipo[1]} for tipo in TIPO_PERMISO if tipo[0] != 'P'],
        },
        safe=False,
    )

def tipo_denuncia(request):
    return JsonResponse(
        {
            "denuncias": [{"id":tipo[0],"descripcion":tipo[1]} for tipo in TIPO_DENUNCIA],
        },
        safe=False,
    )

def ws_localidades(request):
    datos = Localidad.objects.all()
    datos = [d.as_dict() for d in datos]
    return HttpResponse(json.dumps({'Localidades': datos, "cant_registros": len(datos),}), content_type='application/json')
    
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

#Privados
# Create your views here.
@permission_required('operadores.wservices')
def menu(request):
    return render(request, 'menu_wservices.html', {})

#Web Servis generico para todas las apps del sistema
#Si el modelo tiene as_dict, aparece.
@permission_required('operadores.wservices')
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

@permission_required('operadores.individuos')
def csv_aislados(request, localidad_id=None):
    datos = []
    individuos = Individuo.objects.filter(situacion_actual__conducta__in=('D','E'))
    individuos = individuos.select_related('situacion_actual')
    for individuo in individuos:
        datos.append(
            {
                'num_doc': individuo.num_doc,
                'nombres': individuo.nombres,
                'apellidos': individuo.apellidos,
                'estado': individuo.situacion_actual.estado,
                'conducta': individuo.situacion_actual.conducta,
                'fecha_actualizacion': str(individuo.situacion_actual.fecha)[0:16],
                'foto': individuo.get_foto(),
                #'qr': individuo.get_qr(),
            }
        )
    return HttpResponse(json.dumps({'individuos': datos, "cant_registros": len(datos),}), content_type='application/json')