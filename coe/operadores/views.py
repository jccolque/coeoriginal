#Imports de Python
import csv
from datetime import timedelta
#Imports Django
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import permission_required
#Imports extras
from auditlog.models import LogEntry
#Import del proyecto
from core.forms import SearchForm, FechaForm
from informacion.models import Individuo
#Imports de la app
from .functions import obtener_permisos, crear_usuario, auditar_objeto
from .models import SubComite, Operador, EventoOperador
from .forms import SubComiteForm, BuscarOperadorForm, CrearOperadorForm
from .forms import ModOperadorForm, ModPassword, AuditoriaForm
from .forms import AsistenciaForm, ImprimirTarjetasForm

# Create your views here.
@permission_required('operadores.menu_operadores')
def menu(request):
    return render(request, 'menu_operadores.html', {})

#Manejo de SubComites
@permission_required('operadores.subcomites')
def listar_subcomites(request):
    subcomites = SubComite.objects.all()
    subcomites = subcomites.prefetch_related('operadores', 'tareas', 'tareas__eventos')
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            if search:
                subcomites = subcomites.filter(nombre__icontains=search)
    return render(request, 'lista_subcomites.html', {
        'subcomites': subcomites,     
        'has_table': True,
    })

@permission_required('operadores.subcomites')
def ver_subcomite(request, subco_id):
    subcomite = SubComite.objects.prefetch_related(
        'operadores', 'operadores__usuario',
        'tareas', 'tareas__eventos'
        ).get(pk=subco_id)
    form = BuscarOperadorForm()
    if request.method == 'POST':
        form = BuscarOperadorForm(request.POST)
        if form.is_valid():
            operador = form.cleaned_data['operador']
            operador.subcomite = subcomite
            operador.save()
    return render(request, 'ver_subcomite.html', {'subcomite': subcomite, 'form': form, })

@permission_required('operadores.subcomites')
def crear_subcomite(request, subco_id=None):
    subcomite = None
    if subco_id:
        subcomite = SubComite.objects.get(pk=subco_id)
    form = SubComiteForm(instance=subcomite)
    if request.method == "POST":
        form = SubComiteForm(request.POST, instance=subcomite)
        if form.is_valid():
            subcomite = form.save(commit=False)
            subcomite.save()
            return redirect('operadores:listar_subcomites')
    return render(request, "extras/generic_form.html", {'titulo': "Subir Archivo para Carga", 'form': form, 'boton': "Subir", })

#Manejo de Operadores
@permission_required('operadores.operadores')
def listar_operadores(request):
    operadores = Operador.objects.all()
    operadores = operadores.select_related('subcomite', 'usuario')
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            operadores = operadores.filter(
                Q(num_doc__contains=search) |
                Q(apellidos__icontains=search) |
                Q(subcomite__nombre__icontains=search)
            )
    return render(request, 'lista_operadores.html', {
        'operadores': operadores,    
        'has_table': True,
    })

def crear_operador(request):
    form = CrearOperadorForm()
    if request.method == "POST":
        form = CrearOperadorForm(request.POST, request.FILES)
        if form.is_valid():
            operador = form.save(commit=False)
            #Intentamos asignarlo a un usuario
            try:
                operador.individuo = Individuo.objects.get(num_doc=form.cleaned_data['num_doc'])
            except:
                pass
            #Creamos usuario
            if form.cleaned_data['new_user']:#Si marco el check:
                operador.usuario = crear_usuario(operador)
                operador.save()
                return redirect('operadores:modificar_usuario', operador_id=operador.id)
            #Guardamos
            operador.save()
            return redirect('operadores:listar_operadores')
    return render(request, "extras/generic_form.html", {'titulo': "Subir Archivo para Carga", 'form': form, 'boton': "Subir", })

@permission_required('operadores.operadores')
def mod_operador(request, operador_id=None):
    operador = None
    form = ModOperadorForm(permisos_list=obtener_permisos(),)
    if operador_id:
        #Si es para modificar conseguimos las bases
        operador = Operador.objects.get(pk=operador_id)
        usuario = operador.usuario
        permisos_habilitados = [p for p in obtener_permisos(usuario=request.user)]
        id_permisos_habilitados = [p.id for p in obtener_permisos(usuario=usuario)]
        if usuario:
            #Generamos el form
            form = ModOperadorForm(
                instance=operador, 
                permisos_list=permisos_habilitados,
                initial={
                    'username': usuario.username,
                    'permisos': id_permisos_habilitados,
            })
        else:
            form = ModOperadorForm(
                instance=operador, 
                permisos_list=permisos_habilitados,
            )
    if request.method == "POST":
        form = ModOperadorForm(request.POST, request.FILES, instance=operador)
        if form.is_valid():
            operador = form.save(commit=False)
            #Si nos dio un username
            if form.cleaned_data['username']:
                if not operador.usuario:
                    operador.usuario = crear_usuario(operador)
                    operador.save()
                if operador.usuario.username != form.cleaned_data['username']:
                    operador.usuario.username = form.cleaned_data['username']
                    operador.usuario.save()
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

@permission_required('operadores.operadores')
def ver_credencial(request, operador_id):
    operador = Operador.objects.get(id=operador_id)
    return render(request, 'credencial.html', {'operador': operador,})

@permission_required('operadores.operadores')
def imprimir_tarjetas(request):
    form = ImprimirTarjetasForm()
    if request.method == 'POST':
        form = ImprimirTarjetasForm(request.POST)
        if form.is_valid():
            operadores = Operador.objects.filter(id__in=form.cleaned_data['operadores'])
        return render(request, 'tarjetas.html', {'operadores': operadores,})
    return render(request, "extras/generic_form.html", {'titulo': "Seleccione Credenciales", 'form': form, 'boton': "Imprimir", })

@permission_required('operadores.operadores')
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

@permission_required('operadores.operadores')
def desactivar_usuario(request, operador_id):
    operador = Operador.objects.get(pk=operador_id)
    usuario = operador.usuario
    usuario.is_active = False
    usuario.save()
    return redirect('operadores:listar_operadores')

@permission_required('operadores.operadores')
def activar_usuario(request, operador_id):
    operador = Operador.objects.get(pk=operador_id)
    usuario = operador.usuario
    usuario.is_active = True
    usuario.save()
    return redirect('operadores:listar_operadores')

#Ingreso y Egreso
@permission_required('operadores.auditar_operadores')
def registro_asistencia(request):
    form = FechaForm()
    if request.method == 'POST':
        form = FechaForm(request.POST)
        if form.is_valid():
            dia = form.cleaned_data['fecha']
            #begda = timezone.datetime(dia.year, dia.month, dia.day, 0, 0, 0, tzinfo=timezone.get_current_timezone())
            #endda = timezone.datetime(dia.year, dia.month, dia.day, 23, 59, 59, tzinfo=timezone.get_current_timezone())
            asistentes = EventoOperador.objects.filter(fecha__date=dia)
            asistentes = asistentes.select_related('operador', 'operador__subcomite')
            #Procesamos data
            ingresos = {i.operador.id: i for i in asistentes if i.tipo=='I'}#Va a ir pisando hasta dejar solo el ultimo
            egresos = {e.operador.id: e for e in asistentes if e.tipo=='E'}#Va a ir pisando hasta dejar solo el ultimo
            asistentes = [a.operador for a in asistentes]
            asistentes = list(dict.fromkeys(asistentes))
            return render(request, 'registro_asistencia.html', {
                    'asistentes': asistentes,
                    'ingresos': ingresos,
                    'egresos': egresos,
                })
    return render(request, "extras/generic_form.html", {'titulo': "Registro de Asistencia", 'form': form, 'boton': "Generar Reporte", })

@permission_required('operadores.auditar_operadores')
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
    return render(request, 'listar_presentes.html', {
        'presentes': presentes,
        'has_table': True,
    })

@permission_required('operadores.auditar_operadores')
def checkin(request):
    form = AsistenciaForm()
    if request.method == 'POST':
        form = AsistenciaForm(request.POST)
        if form.is_valid():
            evento = EventoOperador(operador=form.operador)
            evento.save()
            return redirect('operadores:ingreso', operador_id=evento.operador.id)
    return render(request, "extras/generic_form.html", {'titulo': "Modificar Usuario", 'form': form, 'boton': "Modificar", })

@permission_required('operadores.auditar_operadores')
def ingreso(request, operador_id):
    operador = Operador.objects.get(id=operador_id)
    return render(request, 'ingreso_operador.html', {'operador': operador,})

@permission_required('operadores.auditar_operadores')
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
            return render(request, "auditoria.html", {
                'usuario': usuario,
                'begda': begda, 'endda': endda,
                'registros': registros,})
    #Lanzamos form basico
    return render(request, "extras/generic_form.html", {'titulo': "Auditoria Usuario", 'form': form, 'boton': "Auditar", })

@permission_required('operadores.auditar_operadores')
def auditar_cambios(request, content_id, object_id):
    #Obtenemos modelo
    modelo = ContentType.objects.get(pk=content_id).model_class()
    #Obtenemos Objeto a auditar
    objeto = modelo.objects.get(pk=object_id)
    #Obtenemos registros de cambios
    registros = auditar_objeto(objeto)
    #Lanzamos muestra:
    return render(request, 'auditar_objeto.html', {
        'objeto': objeto,
        'registros': registros,
    })

@permission_required('operadores.auditar_operadores')
def asistencia(request, operador_id):
    operador = Operador.objects.get(pk=operador_id)
    #Obtenemos los ingresos y egresos
    registros = EventoOperador.objects.filter(operador=operador)
    registros = registros.order_by('fecha')
    #Generamos las asistencias:
    ingresos = registros.filter(tipo='I')
    egresos = registros.filter(tipo='E')
    #Preparamos lista de resultados
    asistencias = []
    #Generamos listado de los que permanecen en el edificio
    for ingreso in ingresos:
        asistencia = [
            ingreso.fecha,
            egresos.filter(fecha__gt=ingreso.fecha).first(),
        ]
        #Calculamos salida
        if asistencia[1]:#Si cargo egreso
            asistencia[1] = asistencia[1].fecha
            tiempo = int((asistencia[1] - asistencia[0]).total_seconds() / 3600)
            if tiempo > 24:
                asistencia[1] = 'Sin Registrar'
                asistencia = [
                    asistencia[0].date(),
                    asistencia[0].time(),
                ]
            else:
                asistencia.append(tiempo)
                asistencia = [
                    asistencia[0].date(),
                    asistencia[0].time(),
                    asistencia[1].time(),
                    asistencia[2],
                ]
        asistencias.append(asistencia)
    return render(request, 'asistencias.html', {
        'operador': operador,
        'asistencias': asistencias,
        'cantidad': len(asistencias),
    })

#Interno
@permission_required('operadores.operadores')
def csv_operadores(request):
    operadores = Operador.objects.all()
    operadores = operadores.select_related('usuario', 'subcomite')
    #Iniciamos la creacion del csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="operadores.csv"'
    writer = csv.writer(response)
    writer.writerow(['REPORTE DE INVENTARIO'])
    writer.writerow(['SUBCOMITE', 'NIVEL DE ACCESO', 'TIPO DOC', 'NUM DOC', 'APELLIDO', 'NOMBRE', 'EMAIL', 'TELEFONO', 'USUARIO'])
    for operador in operadores:
        if operador.subcomite:
            tmp_subcomite = operador.subcomite.nombre
        else:
            tmp_subcomite = 'NO ASIGNADO'
        if operador.usuario:
            tmp_usuario = operador.usuario.username
        else:
            tmp_usuario = 'NO POSEE'
        writer.writerow([
            tmp_subcomite,
            operador.get_nivel_acceso_display(),
            operador.tipo_doc,
            operador.num_doc,
            operador.apellidos,
            operador.nombres,
            operador.email,
            operador.telefono,
            tmp_usuario,
        ])        
    #Enviamos el archivo para descargar
    return response