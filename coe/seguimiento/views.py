#Imports Django
from datetime import timedelta
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
#Imports del proyecto
from coe.settings import GEOPOSITION_GOOGLE_MAPS_API_KEY
from coe.constantes import DIAS_CUARENTENA
from core.decoradores import superuser_required
from core.functions import date2str
from core.forms import SearchForm, JustificarForm
from georef.models import Nacionalidad
from georef.models import Ubicacion
from operadores.functions import obtener_operador
from informacion.models import Individuo, SignosVitales, Relacion
from informacion.models import Situacion
from informacion.models import Seguimiento
from informacion.forms import SeguimientoForm
from app.models import AppData
#imports de la app
from .models import Vigia
from .forms import NuevoVigia, NuevoIndividuo
from .functions import obtener_bajo_seguimiento

#Menu
@permission_required('operadores.seguimiento')
def menu_seguimiento(request):
    return render(request, 'menu_seguimiento.html', {})

@permission_required('operadores.seguimiento_admin')
def lista_seguimientos(request):
    #Obtenemos los registros
    individuos = Individuo.objects.filter(seguimientos__tipo__in=('I','L', 'ET'))
    individuos = individuos.exclude(seguimientos__tipo='FS')
    #Optimizamos las busquedas
    individuos = individuos.select_related('nacionalidad')
    individuos = individuos.select_related('domicilio_actual', 'situacion_actual', 'seguimiento_actual')
    individuos = individuos.prefetch_related('atributos', 'sintomas')
    #Traemos seguimientos terminados para descartar
    #last12hrs = timezone.now() - timedelta(hours=12)
    #individuos = individuos.exclude(seguimientos__fecha__gt=last12hrs)
    #Lanzamos reporte
    return render(request, "listado_seguimiento.html", {
        'individuos': individuos,
        'has_table': True,
    })

#Administracion
@permission_required('operadores.seguimiento_admin')
def lista_sin_vigias(request):
    sin_vigia = obtener_bajo_seguimiento()
    sin_vigia = sin_vigia.filter(vigilador=None)
    return render(request, "listado_seguimiento.html", {
        'individuos': sin_vigia,
        'has_table': True,
    })


@permission_required('operadores.seguimiento_admin')
def asignar_vigia(request, individuo_id):
    form = AsignarVigia()
    if request.method == "POST":
        form = AsignarVigia(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            geoperador = form.cleaned_data['geoperador']
            geoperador.controlados.add(individuo)
            return redirect('geotracking:lista_sin_geoperador')
    return render(request, "extras/generic_form.html", {'titulo': "Asignar Controlador", 'form': form, 'boton': "Asignar", })

@permission_required('operadores.seguimiento_admin')
def lista_vigias(request):
    vigias = Vigia.objects.all()
    vigias = vigias.select_related('operador', 'operador__usuario')
    vigias = vigias.prefetch_related('controlados')
    #Lanzamos listado
    return render(request, "lista_vigias.html", {
        'vigias': vigias,
        'has_table': True,
    })

@permission_required('operadores.seguimiento_admin')
def agregar_vigia(request):
    form = NuevoVigia()
    if request.method == "POST":
        form = NuevoVigia(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seguimiento:lista_vigias')
    return render(request, "extras/generic_form.html", {'titulo': "Habilitar Nuevo Vigia", 'form': form, 'boton': "Habilitar", })

@permission_required('operadores.seguimiento_admin')
def del_vigia(request, vigia_id):
    vigia = Vigia.objects.get(pk=vigia_id)
    if request.method == "POST":
        #Asignamos todos sus controlados a otras personas
        for controlado in vigia.controlados.all():
            try:
                nuevo_vigia = Vigia.objects.exclude(pk=vigia.pk).annotate(cantidad=Count('controlados')).order_by('cantidad').first()
                nuevo_vigia.controlados.add(controlado)
            except:
                print("No existen geoperadores, quedo huerfano.")
        #Lo damos de baja:
        vigia.delete()
        return redirect('seguimiento:lista_vigias')
    return render(request, "extras/confirmar.html", {
            'titulo': "Eliminar Vigilante",
            'message': "Se reasignaran "+str(vigia.controlados.count())+" Individuos.",
            'has_form': True,
        }
    )

@permission_required('operadores.seguimiento')
def agregar_vigilado(request, vigia_id):
    form = NuevoIndividuo()
    if request.method == "POST":
        form = NuevoIndividuo(request.POST)
        if form.is_valid():
            vigia = Vigia.objects.get(pk=vigia_id)
            vigia.controlados.add(form.cleaned_data['individuo'])
            return redirect('geotracking:ver_panel', vigia_id=vigia.id)
    return render(request, "extras/generic_form.html", {'titulo': "Agregar Individuo Seguido", 'form': form, 'boton': "Agregar", })

@permission_required('operadores.seguimiento')
def quitar_vigilado(request, vigia_id, individuo_id):
    #Obtenemos vigia
    vigia = Vigia.objects.get(pk=vigia_id)
    #Obtenemos individuo a dar de baja
    individuo = Individuo.objects.get(pk=individuo_id)
    #Damos de baja
    vigia.controlados.remove(individuo)
    return redirect('geotracking:ver_panel', vigia_id=vigia.id)

#Panel
@permission_required('operadores.seguimiento')
def panel_vigia(request, vigia_id=None):
    #Obtenemos el operador en cuestion
    if vigia_id:
        vigia = Vigia.objects.get(pk=vigia_id)
    else:
        operador = obtener_operador(request)
        try:
            vigia = operador.vigia
        except:
            return render(request, 'extras/error.html', {
            'titulo': 'No existe Panel de Vigilancia',
            'error': "Usted no es un Vigilante Habilitado, si deberia tener acceso a esta seccion, por favor contacte a los administradores.",
        })
    #Buscamos Alertas
    last12hrs = timezone.now() - timedelta(hours=12)
    individuos = vigia.controlados.filter(seguimiento_actual__fecha__lt=last12hrs)
    #Optimizamos
    individuos = individuos.select_related(
        'situacion_actual',
        'domicilio_actual', "domicilio_actual__localidad"
    )
    #Lanzamos panel
    return render(request, "panel_vigia.html", {
        'vigia': vigia,
        'individuos': individuos,
        'refresh': True,
        'has_table': True,
    })

@permission_required('operadores.seguimiento')
def ver_seguimiento(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    return render(request, "ver_seguimiento.html", {
        'individuo': individuo,
        }
    )

#Otros listados
@permission_required('operadores.individuos')
def lista_autodiagnosticos(request):
    individuos = []
    appdatas = AppData.objects.all().order_by('-estado')
    appdatas = appdatas.select_related('individuo')
    appdatas = appdatas.prefetch_related('individuo__situacion_actual')
    appdatas = appdatas.order_by('estado')
    for appdata in appdatas:
        individuos.append(appdata.individuo)
    return render(request, "lista_autodiagnosticos.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def lista_aislados(request):
    individuos = Individuo.objects.filter(domicilio_actual__aislamiento=True)
    individuos = individuos.exclude(domicilio_actual__ubicacion=None)
    #Optimizamos
    individuos = individuos.select_related('nacionalidad')
    individuos = individuos.select_related('situacion_actual')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__ubicacion')
    individuos = individuos.select_related('appdata')
    #Lanzamos reporte
    return render(request, "lista_aislados.html", {
        'individuos': individuos,
        'has_table': True,
    })


#ALTAS SEGUIMIENTO
@permission_required('operadores.seguimiento_admin')
def esperando_alta_seguimiento(request):
    pass

@permission_required('operadores.seguimiento_admin')
def altas_seguimiento(request):
    pass