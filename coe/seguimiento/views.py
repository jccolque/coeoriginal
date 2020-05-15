#Imports de python
from datetime import timedelta
#Imports Django
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.files.base import File
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
from informacion.models import Situacion, Documento
from informacion.forms import BuscarIndividuoSeguro
from app.models import AppData, AppNotificacion
from background.functions import crear_progress_link
#imports de la app
from .models import Seguimiento, Vigia
from .forms import SeguimientoForm, NuevoVigia, NuevoIndividuo
from .functions import obtener_bajo_seguimiento
from .functions import realizar_alta, creamos_doc_alta
from .tasks import altas_masivas

#Publico
def buscar_alta_aislamiento(request):
    form = BuscarIndividuoSeguro()
    if request.method == 'POST':
        form = BuscarIndividuoSeguro(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.filter(
                num_doc=form.cleaned_data['num_doc'],
                apellidos__icontains=form.cleaned_data['apellido']).first()
            if individuo:
                alta = individuo.documentos.filter(tipo='AC').first()
                if alta:
                    return redirect(alta.archivo.url)
                else:
                    if individuo.situacion_actual.conducta in ('D', 'E'):
                        form.add_error(None, "El individuo no cuenta con Alta de Cuarentena.")
                    else:
                        form.add_error(None, "El individuo no se encuentra en situacion de Aislamiento.")
            else:
                form.add_error(None, "No se ha encontrado a Nadie con esos Datos.")
    return render(request, "buscar_permiso.html", {'form': form, })

#Menu
@permission_required('operadores.seguimiento')
def menu_seguimiento(request):
    return render(request, 'menu_seguimiento.html', {
        'es_vigia': Vigia.objects.filter(operador=obtener_operador(request)).exists(),
    })

#Administracion de Seguimientos
#Seguimiento
@permission_required('operadores.individuos')
def cargar_seguimiento(request, individuo_id, seguimiento_id=None, tipo=None):
    seguimiento = None
    if seguimiento_id:
        seguimiento = Seguimiento.objects.get(pk=seguimiento_id)
    individuo = Individuo.objects.get(pk=individuo_id)
    form = SeguimientoForm(instance=seguimiento, initial={'individuo': individuo, 'tipo': tipo})
    if request.method == "POST":
        form = SeguimientoForm(request.POST, instance=seguimiento)
        if form.is_valid():
            seguimiento = form.save(commit=False)
            seguimiento.individuo = individuo
            form.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Seguimiento", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def del_seguimiento(request, seguimiento_id=None):
    seguimiento = Seguimiento.objects.get(pk=seguimiento_id)
    individuo = seguimiento.individuo
    seguimiento.delete()
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Listados
@permission_required('operadores.seguimiento_admin')
def lista_seguimientos(request):
    #Obtenemos los registros
    individuos = obtener_bajo_seguimiento()
    #Filtramos por los que tienen vigia
    individuos = individuos.exclude(vigiladores=None)
    #Optimizamos las busquedas
    individuos = individuos.select_related('nacionalidad')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
    individuos = individuos.select_related('situacion_actual', 'seguimiento_actual')
    individuos = individuos.prefetch_related('vigiladores', 'vigiladores__operador')
    #Traemos seguimientos terminados para descartar
    #last12hrs = timezone.now() - timedelta(hours=12)
    #individuos = individuos.exclude(seguimientos__fecha__gt=last12hrs)
    #Lanzamos reporte
    return render(request, "lista_seguimientos.html", {
        'individuos': individuos,
        'has_table': True,
    })

#Administracion
@permission_required('operadores.seguimiento_admin')
def lista_sin_vigias(request):
    individuos = obtener_bajo_seguimiento()
    individuos = individuos.filter(vigiladores=None)
    #Optimizamos las busquedas
    individuos = individuos.select_related('nacionalidad')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
    individuos = individuos.select_related('situacion_actual', 'seguimiento_actual')
    individuos = individuos.prefetch_related('vigiladores', 'vigiladores__operador')
    #Lanzamos Reporte
    return render(request, "lista_seguimientos.html", {
        'individuos': individuos,
        'has_table': True,
    })


@permission_required('operadores.seguimiento_admin')
def asignar_vigia(request, individuo_id):
    form = AsignarVigia()
    if request.method == "POST":
        form = AsignarVigia(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            vigia = form.cleaned_data['vigia']
            vigia.controlados.add(individuo)
            return redirect('seguimiento:lista_sin_vigias')
    return render(request, "extras/generic_form.html", {'titulo': "Asignar Controlador", 'form': form, 'boton': "Asignar", })

@permission_required('operadores.seguimiento_admin')
def lista_vigias(request):
    vigias = Vigia.objects.all()
    vigias = vigias.select_related('operador', 'operador__usuario')
    vigias = vigias.prefetch_related('controlados')
    #Obtenemos valor:
    limite = timezone.now() - timedelta(hours=12)
    vigias = vigias.annotate(alertas=Count('controlados', controlados__seguimiento_actual__fecha__lt=limite))
    #Lanzamos listado
    return render(request, "lista_vigias.html", {
        'vigias': vigias,
        'has_table': True,
    })

@permission_required('operadores.seguimiento_admin')
def agregar_vigia(request, vigia_id=None):
    vigia = None
    if vigia_id:
        vigia = Vigia.objects.get(pk=vigia_id)
    form = NuevoVigia(instance=vigia)
    if request.method == "POST":
        form = NuevoVigia(request.POST, instance=vigia)
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
                pass
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
            return redirect('seguimiento:ver_panel', vigia_id=vigia.id)
    return render(request, "extras/generic_form.html", {'titulo': "Agregar Individuo Seguido", 'form': form, 'boton': "Agregar", })

@permission_required('operadores.seguimiento')
def quitar_vigilado(request, vigia_id, individuo_id):
    #Obtenemos vigia
    vigia = Vigia.objects.get(pk=vigia_id)
    #Obtenemos individuo a dar de baja
    individuo = Individuo.objects.get(pk=individuo_id)
    #Damos de baja
    vigia.controlados.remove(individuo)
    return redirect('seguimiento:ver_panel', vigia_id=vigia.id)

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
    individuos = vigia.controlados.filter(Q(seguimiento_actual__fecha__lt=last12hrs) | Q(seguimiento_actual=None))
    #Optimizamos
    individuos = individuos.select_related(
        'situacion_actual',
        'domicilio_actual', "domicilio_actual__localidad",
        'seguimiento_actual',
    )
    #Ordenamos por fecha
    individuos = individuos.order_by('seguimiento_actual__fecha')
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
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
    individuos = individuos.select_related('appdata')
    individuos = individuos.prefetch_related('vigiladores', 'vigiladores__operador')
    #Lanzamos reporte
    return render(request, "lista_seguimientos.html", {
        'individuos': individuos,
        'has_table': True,
    })

#ALTAS SEGUIMIENTO
@permission_required('operadores.seguimiento_admin')
def esperando_alta_seguimiento(request):
    if request.method == 'POST':#Si mandaron grupo de altas masivas
        #Obtenemos al operador
        operador = obtener_operador(request)
        #Obtenemos los individuos marcados
        ids = request.POST.getlist('alta')
        #Definimos la tarea
        tarea = crear_progress_link(str(operador)+":altas_masivas("+str(timezone.now())[0:16].replace(' ','')+")")
        #Fragmentamos los usuarios en grupos
        frag_size = 10#Dividimos en fragmentos de 25
        segmentos = [ids[x:x+frag_size] for x in range(0, len(ids), frag_size)]
        #Lanzamos la tarea
        for segmento in segmentos:
            altas_masivas(segmento, operador.pk, queue=tarea)
        return redirect('background:ver_background', task_name=tarea)
    else:
        individuos = Individuo.objects.filter(situacion_actual__conducta__in=('D', 'E'))
        #Optimizamos
        individuos = individuos.select_related('nacionalidad')
        individuos = individuos.select_related('situacion_actual')
        individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
        individuos = individuos.select_related('appdata')
        individuos = individuos.prefetch_related('vigiladores', 'vigiladores__operador')
        #Filtramos los que falta solo 2 dias
        limite = timezone.now() - timedelta(days=DIAS_CUARENTENA - 2)
        individuos = individuos.filter(situacion_actual__fecha__lt=limite)
        #Lanzamos reporte
        return render(request, "lista_para_alta.html", {
            'individuos': individuos,
            'has_table': True,
        })

@permission_required('operadores.seguimiento_admin')
def dar_alta(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    if request.method == "POST":
        #Obtenemos al operador
        realizar_alta(individuo, obtener_operador(request))
        #Volvemos a la lista
        return redirect('seguimiento:esperando_alta_seguimiento')
    return render(request, "extras/confirmar.html", {
            'titulo': "Dar de Alta a " + str(individuo),
            'message': "Si realiza esta accion quedara registrada por su usuario.",
            'has_form': True,
        }
    )

@permission_required('operadores.seguimiento_admin')
def altas_realizadas(request):
    individuos = Individuo.objects.filter(documentos__tipo='AC')
    #Optimizamos
    individuos = individuos.select_related('nacionalidad')
    individuos = individuos.select_related('situacion_actual')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
    individuos = individuos.select_related('appdata')
    individuos = individuos.prefetch_related('vigiladores', 'vigiladores__operador')
    #Lanzamos reporte
    return render(request, "lista_altas_realizadas.html", {
        'individuos': individuos,
        'has_table': True,
    })
