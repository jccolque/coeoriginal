#Imports PYthon
import json
#Imports Django
from django.apps import apps
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required
from django.core import serializers
#Imports del proyecto
from georef.models import Provincia, Localidad, Barrio
from informacion.choices import TIPO_ESTADO, TIPO_CONDUCTA
from informacion.models import Individuo, Situacion, Domicilio
from permisos.choices import TIPO_PERMISO
from consultas.choices import TIPO_DENUNCIA
from seguimiento.models import DatosGis

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
    #Filtramos jujuy:
    jujuy = Provincia.objects.get(id_infragob=38)
    #Obtenemos todas las localidades de jujuy
    datos = Localidad.objects.filter(departamento__provincia=jujuy)
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

@permission_required('operadores.individuos')
def ws_seguimientos(request):
    #Generamos diccionario
    data = {}
    #Obtenemos datos a procesar
    individuos = Individuo.objects.exclude(seguimientos=None)
    individuos = individuos.select_related("situacion_actual", "domicilio_actual", "domicilio_actual__localidad")
    individuos = individuos.prefetch_related("seguimientos", "seguimientos__operador")
    #Generamos un subdict por cada individuo
    for individuo in individuos:
        ind = {}
        ind["num_doc"] = individuo.num_doc
        ind["apellidos"] = individuo.apellidos
        ind["situacion"] = str(individuo.get_situacion())
        ind["nombres"] = individuo.nombres
        ind["telefono"] = individuo.telefono
        if individuo.domicilio_actual:
            ind["domicilio"] = individuo.domicilio_actual.calle + ' ' + individuo.domicilio_actual.numero
            ind["localidad"] = str(individuo.domicilio_actual.localidad.nombre)
        ind["seguimientos"] = []
        for seguimiento in individuo.seguimientos.all():
            seg = {}
            seg["tipo"] = seguimiento.get_tipo_display()
            seg["aclaracion"] = seguimiento.aclaracion
            seg["operador"] = str(seguimiento.operador)
            seg["fecha"] = str(seguimiento.fecha)
            ind["seguimientos"].append(seg)
        data[individuo.num_doc] = ind
    #Entregamos json
    return HttpResponse(json.dumps({'Individuos': data, "cant_registros": len(data),}), content_type='application/json')

@permission_required('operadores.individuos')
def ws_atributos(request):
    #Generamos diccionario
    data = {}
    #Obtenemos datos a procesar
    individuos = Individuo.objects.exclude(atributos=None)
    individuos = individuos.select_related("domicilio_actual", "domicilio_actual__localidad")
    individuos = individuos.prefetch_related("atributos")
    #Generamos un subdict por cada individuo
    for individuo in individuos:
        ind = {}
        ind["num_doc"] = individuo.num_doc
        ind["apellidos"] = individuo.apellidos
        ind["situacion"] = str(individuo.get_situacion())
        ind["nombres"] = individuo.nombres
        ind["telefono"] = individuo.telefono
        if individuo.domicilio_actual:
            ind["domicilio"] = individuo.domicilio_actual.calle + ' ' + individuo.domicilio_actual.numero
            ind["localidad"] = str(individuo.domicilio_actual.localidad.nombre)
        ind["atributos"] = []
        for atributo in individuo.atributos.all():
            atrib = {}
            atrib["tipo"] = atributo.get_tipo_display()
            atrib["aclaracion"] = atributo.aclaracion
            atrib["fecha"] = str(atributo.fecha)
            ind["atributos"].append(atrib)
        data[individuo.num_doc] = ind
    #Entregamos json
    return HttpResponse(json.dumps({'Individuos': data, "cant_registros": len(data),}), content_type='application/json')

@permission_required('operadores.individuos')
def ws_llamadas(request):
    #Generamos diccionario
    data = {}
    #Obtenemos datos a procesar
    individuos = Individuo.objects.exclude(seguimientos=None)
    individuos = Individuo.objects.filter(seguimientos__tipo='L')#solo las llamadas
    individuos = individuos.select_related("situacion_actual", "domicilio_actual", "domicilio_actual__localidad")
    individuos = individuos.prefetch_related("seguimientos", "seguimientos__operador")
    #Generamos un subdict por cada individuo
    for individuo in individuos:
        ind = {}
        ind["num_doc"] = individuo.num_doc
        ind["apellidos"] = individuo.apellidos
        ind["situacion"] = str(individuo.get_situacion())
        ind["nombres"] = individuo.nombres
        ind["telefono"] = individuo.telefono
        if individuo.domicilio_actual:
            ind["domicilio"] = individuo.domicilio_actual.calle + ' ' + individuo.domicilio_actual.numero
            ind["localidad"] = str(individuo.domicilio_actual.localidad.nombre)
        ind["llamadas"] = []
        llamadas = [l for l in individuo.seguimientos.all() if l.tipo == 'L']
        for seguimiento in llamadas:
            seg = {}
            seg["tipo"] = seguimiento.get_tipo_display()
            seg["aclaracion"] = seguimiento.aclaracion
            seg["fecha"] = str(seguimiento.fecha)
            seg["vigia"] = str(seguimiento.operador)
            try:
                seg["vigia_doc"] = str(seguimiento.operador.num_doc)
                seg["vigia_tipo"] = str(seguimiento.operador.vigia.tipo)
            except:
                seg["tipo_vigia"] = "No registrado"
            ind["llamadas"].append(seg)
        data[individuo.num_doc] = ind
    #Entregamos json
    return HttpResponse(json.dumps({'Individuos': data, "cant_registros": len(data),}), content_type='application/json')

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
def ws_aislados(request, localidad_id=None):
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


@permission_required('operadores.individuos')
def ws_ocupacion(request):
    datos = []
    doms = Domicilio.objects.exclude(ubicacion=None)
    doms = doms.select_related('ubicacion', 'ubicacion__localidad')
    doms = doms.select_related('individuo', 'individuo__nacionalidad')
    for dom in doms:
        datos.append(
            {
                #Datos del pasajero
                'num_doc': dom.individuo.num_doc,
                'nombres': dom.individuo.nombres,
                'apellidos': dom.individuo.apellidos,
                #Datos del hotel
                'fecha_ingreso': str(dom.fecha.date()),
                'hotel': dom.ubicacion.nombre,
                'localidad': dom.ubicacion.localidad.nombre,
                'aclaracion': dom.aclaracion,
            }
        )
    return HttpResponse(json.dumps({'alojamientos': datos, "cant_registros": len(datos),}), content_type='application/json')

def ws_confirmados_gis(request):
    datos = []
    dgis = DatosGis.objects.all()   
    for dgi in dgis:
        datos.append(
            {
                'localidad': dgi.localidad.nombre,
                'latitud': str(dgi.localidad.latitud),
                'longitud': str(dgi.localidad.longitud),
                'turno': dgi.get_turno_display(),
                'fecha_carga': str(dgi.fecha_carga.date()),
                'confirmados': dgi.confirmados,                
            }
        )
    return HttpResponse(json.dumps({'confirmados_gis': datos, "cantidad_registros": len(datos),}), content_type='application/json')


def ws_recuperados_gis(request):
    datos = []
    dgis = DatosGis.objects.all()   
    for dgi in dgis:
        datos.append(
            {    
                'localidad': dgi.localidad.nombre,
                'longitud': str(dgi.localidad.longitud),
                'latitud': str(dgi.localidad.latitud),
                'turno': dgi.get_turno_display(),
                'fecha_carga': str(dgi.fecha_carga.date()),                
                'recuperados': dgi.recuperados,                
            }
        )
    return HttpResponse(json.dumps({'recuperados_gis': datos, "cantidad_registros": len(datos),}), content_type='application/json')

def ws_fallecidos_gis(request):
    datos = []
    dgis = DatosGis.objects.all()   
    for dgi in dgis:
        datos.append(
            {    
                'localidad': dgi.localidad.nombre,
                'longitud': str(dgi.localidad.longitud),
                'latitud': str(dgi.localidad.latitud),
                'turno': dgi.get_turno_display(),
                'fecha_carga': str(dgi.fecha_carga.date()),                
                'fallecidos': dgi.fallecidos,                
            }
        )
    return HttpResponse(json.dumps({'fallecidos_gis': datos, "cantidad_registros": len(datos),}), content_type='application/json')

def ws_pcr_gis(request):
    datos = []
    dgis = DatosGis.objects.all()   
    for dgi in dgis:
        datos.append(
            {    
                'localidad': dgi.localidad.nombre,
                'longitud': str(dgi.localidad.longitud),
                'latitud': str(dgi.localidad.latitud),
                'turno': dgi.get_turno_display(),
                'fecha_carga': str(dgi.fecha_carga.date()),                
                'pcr': dgi.pcr,                
            }
        )
    return HttpResponse(json.dumps({'pcr_gis': datos, "cantidad_registros": len(datos),}), content_type='application/json')

