#Imports Django
import json
from django.utils import timezone
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
#Imports del proyecto
from georef.models import Localidad, Barrio
from informacion.choices import TIPO_ESTADO, TIPO_CONDUCTA
from informacion.models import Situacion
from permisos.choices import TIPO_PERMISO

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