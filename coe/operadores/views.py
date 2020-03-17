#Imports de Python
import pytz
from datetime import timedelta
#Imports Django
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import permission_required
#Imports extras
from auditlog.models import LogEntry
#Import del proyecto
from core.functions import paginador
from core.forms import SearchForm, FechaForm
#Imports de la app
from .functions import obtener_permisos
from .models import SubComite, Operador, EventoOperador
from .forms import SubComiteForm, CrearOperadorForm
from .forms import ModOperadorForm, ModPassword, AuditoriaForm
from .forms import AsistenciaForm
# Create your views here.
@permission_required('operadores.menu_operadores')
def menu(request):
    return render(request, 'menu_operadores.html', {})

#Manejo de SubComites
@permission_required('operadores.ver_subcomite')
def listar_subcomites(request):
    subcomites = SubComite.objects.all()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            if search:
                subcomites = subcomites.filter(nombre__icontains=search)
    return render(request, 'users/lista_subcomites.html', {'subcomites': subcomites, })

@permission_required('operadores.ver_subcomite')
def ver_subcomite(request, subco_id):
    subcomite = SubComite.objects.get(pk=subco_id)
    return render(request, 'users/ver_subcomite.html', {'subcomite': subcomite, })

@permission_required('operadores.crear_subcomite')
def crear_subcomite(request):
    form = SubComiteForm()
    if request.method == "POST":
        form = SubComiteForm(request.POST, request.FILES)
        if form.is_valid():
            subcomite = form.save(commit=False)
            subcomite.save()
            return redirect('operadores:listar_subcomites')
    return render(request, "extras/generic_form.html", {'titulo': "Subir Archivo para Carga", 'form': form, 'boton': "Subir", })

#Manejo de Operadores
@permission_required('operadores.listar_operadores')
def listar_operadores(request):
    operadores = Operador.objects.all()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            operadores = operadores.filter(
                Q(usuario__username__icontains=search) |
                Q(usuario__last_name__icontains=search)
            )
    operadores = paginador(request, operadores)
    return render(request, 'users/listar_operadores.html', {'operadores': operadores,})

def crear_operador(request):
    form = CrearOperadorForm()
    if request.method == "POST":
        form = CrearOperadorForm(request.POST, request.FILES)
        if form.is_valid():
            operador = form.save(commit=False)
            operador.save()
            return redirect('operadores:listar_operadores')
    return render(request, "extras/generic_form.html", {'titulo': "Subir Archivo para Carga", 'form': form, 'boton': "Subir", })

@permission_required('operadores.crear_operador')
def mod_operador(request, operador_id=None):
    operador = None
    form = ModOperadorForm(permisos_list=obtener_permisos(),)
    if operador_id:
        #Si es para modificar conseguimos las bases
        operador = Operador.objects.get(pk=operador_id)
        usuario = operador.usuario
        if usuario:
            #Generamos el form
            form = ModOperadorForm(
                instance=operador, 
                permisos_list=obtener_permisos(),
                initial={
                    'username': usuario.username,
                    'permisos': [p.id for p in obtener_permisos(usuario=usuario)],
            })
        else:
            form = ModOperadorForm(
                instance=operador, 
                permisos_list=obtener_permisos(),
            )
    if request.method == "POST":
        form = ModOperadorForm(request.POST, request.FILES, instance=operador)
        if form.is_valid():
            operador = form.save(commit=False)
            #Primero creamos el usuario
            #Que sea nivel_seg = "R"
            if form.cleaned_data['username']:
                if not usuario:
                    usuario = User()
                    usuario.username = form.cleaned_data['username']
                    usuario.is_active=False
                #Cargamos datos del Form
                usuario.email = operador.email
                usuario.first_name = operador.nombres
                usuario.last_name = operador.apellidos
                usuario.is_staff=True                    
                usuario.save()
                operador.usuario = usuario
            #Reiniciamos sus permisos:
            if usuario:
                for permiso in obtener_permisos():
                    usuario.user_permissions.remove(permiso)
            for permiso in request.POST.getlist('permisos'):
                usuario.user_permissions.add(permiso)
            usuario.save()
            operador.save()
            return redirect('operadores:listar_operadores')
    return render(request, "extras/generic_form.html", {'titulo': "Subir Archivo para Carga", 'form': form, 'boton': "Subir", })

@permission_required('operadores.ver_credencial')
def ver_credencial(request, operador_id):
    operador = Operador.objects.get(id=operador_id)
    return render(request, 'credencial.html', {'operador': operador,})

@permission_required('operadores.modificar_operador')
def cambiar_password(request, operador_id):
    operador = Operador.objects.get(pk=operador_id)
    usuario = operador.usuario
    form = ModPassword(initial={'username': usuario.username, })
    if request.method == 'POST':
        form = ModPassword(request.POST)
        if form.is_valid():
            usuario.password = make_password(form.cleaned_data['passwd1'])
            usuario.save()
            return redirect('operadores:listar_operadores')
    #Sea por ingreso o por salida:
    return render(request, "extras/generic_form.html", {'titulo': "Modificar Usuario", 'form': form, 'boton': "Modificar", })

@permission_required('operadores.modificar_operador')
def desactivar_usuario(request, operador_id):
    operador = Operador.objects.get(pk=operador_id)
    usuario = operador.usuario
    usuario.is_active = False
    usuario.save()
    return redirect('operadores:listar_operadores')

@permission_required('operadores.modificar_operador')
def activar_usuario(request, operador_id):
    operador = Operador.objects.get(pk=operador_id)
    usuario = operador.usuario
    usuario.is_active = True
    usuario.save()
    return redirect('operadores:listar_operadores')

#Ingreso y Egreso
@permission_required('operadores.control_asistencia')
def registro_asistencia(request):
    form = FechaForm()
    if request.method == 'POST':
        form = FechaForm(request.POST)
        if form.is_valid():
            dia = form.cleaned_data['fecha']
            begda = timezone.datetime(dia.year, dia.month, dia.day, 0, 0, 0, tzinfo=timezone.get_current_timezone())
            endda = timezone.datetime(dia.year, dia.month, dia.day, 23, 59, 59, tzinfo=timezone.get_current_timezone())
            asistentes = EventoOperador.objects.filter(fecha__range=(begda, endda))
            ingresos = {i.operador.id: i for i in asistentes.filter(tipo='I')}#Va a ir pisando hasta dejar solo el ultimo
            egresos = {e.operador.id: e for e in asistentes.filter(tipo='E')}#Va a ir pisando hasta dejar solo el ultimo
            asistentes = [a.operador for a in asistentes]
            asistentes = list(dict.fromkeys(asistentes))
            return render(request, 'registro_asistencia.html', {
                    'asistentes': asistentes,
                    'ingresos': ingresos,
                    'egresos': egresos,
                })
    return render(request, "extras/generic_form.html", {'titulo': "Registro de Asistencia", 'form': form, 'boton': "Generar Reporte", })

@permission_required('operadores.control_asistencia')
def listado_presentes(request):
    asistentes = EventoOperador.objects.all()#Traemos todos los eventos
    asistentes = asistentes.select_related('operador', 'operador__usuario')#Traemos operador para evitar consultas db
    asistentes = asistentes.order_by('fecha')#Ordenados de mas cerca a mas lejos
    #Si busco, filtramos
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            asistentes = asistentes.filter(
                Q(operador__usuario__first_name__icontains=search) |
                Q(operador__usuario__last_name__icontains=search)
            )
    #Filtramos solo las ultimas 24hrs
    begda = timezone.now() - timedelta(hours=23, minutes=59, seconds=59)
    asistentes = asistentes.filter(fecha__gt=begda)#Solo los de las ultimas 24hrs
    #Obtenemos los dos dict funcionales
    ingresos = {i.operador.id: i for i in asistentes.filter(tipo='I')}#Va a ir pisando hasta dejar solo el ultimo
    egresos = {e.operador.id: e for e in asistentes.filter(tipo='E')}#Va a ir pisando hasta dejar solo el ultimo
    #Preparamos lista de resultados
    presentes = []
    #Generamos listado de los que permanecen en el edificio
    for operador_id, ingreso in ingresos.items():
        if operador_id not in egresos:
            presentes.append(ingreso)
        elif egresos[operador_id].fecha < ingreso.fecha:
            presentes.append(ingreso)
    return render(request, 'listar_presentes.html', {'presentes': presentes,})

@permission_required('operadores.control_asistencia')
def checkin(request):
    form = AsistenciaForm()
    if request.method == 'POST':
        form = AsistenciaForm(request.POST)
        if form.is_valid():
            evento = EventoOperador(operador=form.operador)
            evento.save()
            return redirect('operadores:ingreso', operador_id=evento.operador.id)
    return render(request, "extras/generic_form.html", {'titulo': "Modificar Usuario", 'form': form, 'boton': "Modificar", })

@permission_required('operadores.control_asistencia')
def ingreso(request, operador_id):
    operador = Operador.objects.get(id=operador_id)
    return render(request, 'users/ingreso_operador.html', {'operador': operador,})

@permission_required('operadores.control_asistencia')
def checkout(request, operador_id):
    operador = Operador.objects.get(id=operador_id)
    evento = EventoOperador(operador=operador, tipo='E')
    evento.save()
    return redirect('operadores:listado_presentes')

#Auditoria
@permission_required('operadores.auditar_operadores')
def auditoria(request, user_id=None):
    form = AuditoriaForm()
    if user_id:
        usuario = User.objects.get(id=user_id)
        form = AuditoriaForm(initial={'usuario': usuario, })
    if request.method == "POST":
        form = AuditoriaForm(request.POST)
        if form.is_valid():
            begda = form.cleaned_data['begda']
            endda = form.cleaned_data['endda']
            usuario = form.cleaned_data['usuario']
            #Obtenemos los registros y los filtramos
            registros = LogEntry.objects.filter(actor=usuario)#beneficiarios modificados
            registros = registros.filter(timestamp__range=(begda, endda))
            registros = registros.select_related('content_type')
            return render(request, "users/auditoria.html", {
                'usuario': usuario,
                'begda': begda, 'endda': endda,
                'registros': registros,})
    #Lanzamos form basico
    return render(request, "extras/generic_form.html", {'titulo': "Auditoria Usuario", 'form': form, 'boton': "Auditar", })