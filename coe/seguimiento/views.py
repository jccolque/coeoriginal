#Imports de python
from datetime import datetime, timedelta
#Imports Django
from django.db.models import Q, Count, OuterRef
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.files.base import File
from django.db.models import OuterRef, Subquery, Sum
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
#Imports extras
from auditlog.models import LogEntry
#Imports del proyecto
from coe.settings import GEOPOSITION_GOOGLE_MAPS_API_KEY
from coe.constantes import DIAS_CUARENTENA
from core.decoradores import superuser_required
from core.functions import date2str
from core.forms import SearchForm, JustificarForm
from georef.models import Nacionalidad
from georef.models import Ubicacion
from graficos.functions import obtener_grafico
from operadores.models import Operador
from operadores.functions import obtener_operador
from informacion.choices import TIPO_ATRIBUTO, TIPO_PATOLOGIA
from informacion.models import Individuo, Atributo, Patologia
from informacion.models import SignosVitales, Relacion
from informacion.models import Situacion, Documento
from informacion.models import Vehiculo
from informacion.forms import SearchIndividuoForm, BuscarIndividuoSeguro
from geotracking.models import GeoPosicion
from operadores.functions import obtener_operador
from app.models import AppData, AppNotificacion
from app.functions import activar_tracking, desactivar_tracking
from background.functions import crear_progress_link
#imports de la app
from .models import Seguimiento, Vigia
from .models import OperativoVehicular, TestOperativo
from .forms import SeguimientoForm, NuevoVigia, NuevoIndividuo
from .forms import OperativoForm, TestOperativoForm
from .functions import obtener_bajo_seguimiento
from .functions import realizar_alta
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
                alta = individuo.documentos.filter(tipo='AC').last()
                if alta:
                    try:
                        return redirect(alta.archivo.url)
                    except:
                        form.add_error(None, "El individuo no cuenta con Alta de Cuarentena.")
                else:
                    sit = individuo.get_situacion()
                    if sit.conducta in ('D', 'E'):
                        form.add_error(None, "El individuo no cuenta con Alta de Cuarentena.")
                    else:
                        form.add_error(None, "El individuo no se encuentra en situacion de Aislamiento.")
            else:
                form.add_error(None, "No se ha encontrado a Nadie con esos Datos.")
    return render(request, "buscar_permiso.html", {'form': form, })

def pedir_test(request):
    error = None
    if request.method == 'POST':
        num_doc = request.POST['num_doc']
        try:
            individuo = Individuo.objects.get(num_doc=num_doc, situacion_actual__conducta__in=('D', 'E'))
            if individuo.seguimientos.filter(tipo='PT').exists():
                error = "Usted ya realizo el pedido de Test."
            else:
                individuo.email = request.POST['email']
                individuo.telefono = request.POST['telefono']
                fecha = request.POST['fecha_nacimiento']
                try:
                    individuo.fecha_nacimiento = datetime(int(fecha[6:]),int(fecha[3:5]), int(fecha[0:2]))
                except:
                    pass#No pudimos obtener fecha
                individuo.save()
                #Pedido de Test
                seguimiento = Seguimiento(individuo=individuo)
                seguimiento.tipo = 'PT'
                seguimiento.aclaracion = "Pedido de Test Online"
                seguimiento.save()
                #Patologias:
                for check in request.POST.getlist('patologias'):
                    patologia = Patologia(individuo=individuo)
                    patologia.tipo = check
                    patologia.aclaracion = "Pedido de Test Online"
                    patologia.save()
                #Excepciones:
                for check in request.POST.getlist('excepciones'):
                    atributo = Atributo(individuo=individuo)
                    atributo.tipo = check
                    atributo.aclaracion = "Pedido de Test Online"
                    atributo.save()
                return render(request, "extras/resultado.html", {"texto": "Su pedido fue registrado con exito, pronto lo contactaremos."})
        except:
            error = "Usted no se encuentra en condiciones de Pedir el Test."
    return render(request, "pedir_test.html", {
        'error': error,
        'tipos_patologias': TIPO_PATOLOGIA,
        'tipos_excepciones': [t for t in TIPO_ATRIBUTO if len(t[0]) == 3],
    })

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
    individuo = Individuo.objects.get(pk=individuo_id)
    if seguimiento_id:
        seguimiento = Seguimiento.objects.get(pk=seguimiento_id)
        form = SeguimientoForm(instance=seguimiento)
    else:
        form = SeguimientoForm(initial={'tipo': tipo})
    if request.method == "POST":
        form = SeguimientoForm(request.POST, instance=seguimiento)
        if form.is_valid():
            seguimiento = form.save(commit=False)
            seguimiento.individuo = individuo
            seguimiento.operador = obtener_operador(request)
            form.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Seguimiento", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def del_seguimiento(request, seguimiento_id=None):
    seguimiento = Seguimiento.objects.get(pk=seguimiento_id)
    individuo = seguimiento.individuo
    seguimiento.delete()
    return render(request, "extras/close.html")

#Listados
@permission_required('operadores.seguimiento_admin')
def situacion_vigilancia(request):
    #obtenemos vigilantes
    vigias = Vigia.objects.all()
    #Optimizamos
    vigias = vigias.select_related('operador', 'operador__usuario')
    vigias = vigias.prefetch_related('controlados')
    #Preparamos filtros
    limite_dia = timezone.now() - timedelta(hours=24)
    limite_semana = timezone.now() - timedelta(days=7)
    #Agregamos datos de interes:
    vigias = vigias.annotate(
            cant_controlados=Count('controlados')
        ).annotate(
            alertas=Count(
                'controlados',
                filter=Q(controlados__seguimiento_actual__fecha__lt=limite_dia),
            )
        ).annotate(
            total_seguimientos=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(total_seguimientos=Count('seguimientos_cargados')).values('total_seguimientos')[:1]
            ),
        ).annotate(
            semana_seguimientos=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(total_seguimientos=Count('seguimientos_cargados', filter=Q(seguimientos_cargados__fecha__gt=limite_semana))).values('total_seguimientos')[:1]
            ),
    )
    #Generamos estadisticas para grafico de la ultimas dos semanas:
    limite_2semanas = timezone.now() - timedelta(days=14)
    #Generamos grafico
    graf_vigilancia = obtener_grafico('graf_vigilancia', 'Grafico de Vigilancia', 'L')
    graf_vigilancia.reiniciar_datos()
    #Linea de Seguimientos
    seguimientos = Seguimiento.objects.filter(fecha__gte=limite_2semanas, fecha__lte=timezone.now()).exclude(operador=None)
    segs_dias = {}
    for seguimiento in seguimientos:
        if seguimiento.fecha.date() in segs_dias:
            segs_dias[seguimiento.fecha.date()] += 1
        else:
            segs_dias[seguimiento.fecha.date()] = 1
    for (fecha), cantidad in segs_dias.items():
        graf_vigilancia.bulk_dato(fecha, 'seguimientos', date2str(fecha), cantidad)
    #Linea de Controlados
    situaciones = Situacion.objects.filter(fecha__gte=limite_2semanas, fecha__lte=timezone.now(), conducta__in=('E','D'))
    sits_dias = {}
    for situacion in situaciones:
        if situacion.fecha.date() in sits_dias:
            sits_dias[situacion.fecha.date()] += 1
        else:
            sits_dias[situacion.fecha.date()] = 1
    for fecha, cantidad in sits_dias.items():
        graf_vigilancia.bulk_dato(fecha, 'controlados', date2str(fecha), cantidad)
    graf_vigilancia.bulk_save()
    #Definimos algunos detalles del grafico:
    graf_vigilancia.alto = 500
    #Lanzamos reporte
    return render(request, "situacion_vigilancia.html", {
        'vigias': vigias,
        'has_table': True,
        'graf_vigilancia': graf_vigilancia,
    })

@permission_required('operadores.seguimiento_admin')
def seguimientos_vigia(request, vigia_id):
    vigia = Vigia.objects.all()
    #Optimizamos
    vigia = vigia.select_related('operador', 'operador__usuario')
    vigia = vigia.prefetch_related('controlados')
    vigia = vigia.prefetch_related('operador', 'operador__seguimientos_cargados', 'operador__seguimientos_cargados__individuo')
    #OBtenemos
    vigia = vigia.get(id=vigia_id)
    #Lanzamos reporte
    return render(request, "seguimientos_vigia.html", {
        'vigia': vigia,
        'has_table': True,
    })

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
    return render(request, "lista_seguidos.html", {
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
    return render(request, "lista_seguidos.html", {
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
    vigias = vigias.annotate(alertas=Count('controlados', filter=Q(controlados__seguimiento_actual__fecha__lt=limite)))
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
        'seguimiento_actual', 'seguimiento_actual__operador',
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
    individuo = Individuo.objects.prefetch_related('seguimientos', 'seguimientos__operador')
    individuo= individuo.get(pk=individuo_id)
    return render(request, "ver_seguimiento.html", {
        'individuo': individuo,
        }
    )

#CAZADOR 360
@permission_required('operadores.operativos')
def lista_operativos(request):
    #Operativos Autorizados
    operativos = OperativoVehicular.objects.exclude(estado='E')
    #Optimizamos
    operativos = operativos.select_related('vehiculo')
    operativos = operativos.prefetch_related('cazadores')
    #Lanzamos listado
    return render(request, "lista_operativos.html", {
        'operativos': operativos,
        'refresh': True,
        'has_table': True,
        }
    )

@permission_required('operadores.operativos')
def situacion_operativos(request):
    #Obtenemos operativos Activos:
    operativos = OperativoVehicular.objects.filter(estado='I')
    #Optimizamos
    operativos = operativos.select_related('vehiculo')
    operativos = operativos.prefetch_related('cazadores')
    #Obtenemos ultimas geoposiciones:
    geoposiciones = []
    for operativo in operativos:
        geoposiciones.append(operativo.get_geoposiciones.last())
    #Mostramos
    return render(request, "situacion_operativos.html", {
        'operativo': operativo,
        'geoposiciones': geoposiciones,
        'refresh': (operativo.estado == 'I'),
        'gmkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
        }
    )


@permission_required('operadores.operativos')
def ver_operativo(request, operativo_id):
    #Optimizamos
    operativos = OperativoVehicular.objects.select_related('vehiculo')
    operativos = operativos.prefetch_related('cazadores')
    operativos = operativos.prefetch_related('tests', 'tests__individuo')
    #Buscamos el operativo
    operativo = operativos.get(pk=operativo_id)
    #Mostramos
    return render(request, "panel_operativo.html", {
        'operativo': operativo,
        'refresh': (operativo.estado == 'I'),
        'gmkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
        }
    )

@permission_required('operadores.operativos')
def crear_operativo(request, operativo_id=None):
    operativo = None
    if operativo_id:
        operativo = OperativoVehicular.objects.get(pk=operativo_id)
    form = OperativoForm(instance=operativo)
    if request.method == 'POST':
        form = OperativoForm(request.POST, instance=operativo)
        if form.is_valid():
            operativo = form.save()
            return redirect('seguimiento:ver_operativo', operativo_id=operativo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Crear Operativo", 'form': form, 'boton': "Crear", })

@permission_required('operadores.operativos')
def del_operativo(request, operativo_id):
    operativo = OperativoVehicular.objects.get(pk=operativo_id)
    operativo.estado = 'E'
    operativo.save()
    return redirect('seguimiento:lista_operativos')

@permission_required('operadores.operativos')
def iniciar_operativo(request, operativo_id):
    operativo = OperativoVehicular.objects.get(pk=operativo_id)
    operativo.estado = 'I'
    operativo.fecha_inicio = timezone.now()
    for individuo in operativo.cazadores.all():
        activar_tracking(individuo)
    operativo.fecha_final = None
    operativo.save()
    return redirect('seguimiento:ver_operativo', operativo_id=operativo.id)

@permission_required('operadores.operativos')
def finalizar_operativo(request, operativo_id):
    operativo = OperativoVehicular.objects.get(pk=operativo_id)
    operativo.estado = 'I'
    for individuo in operativo.cazadores.all():
        desactivar_tracking(individuo)
    operativo.fecha_final = timezone.now()
    operativo.estado = 'F'
    operativo.save()
    return redirect('seguimiento:ver_operativo', operativo_id=operativo.id)

@permission_required('operadores.operativos')
def agregar_cazador(request, operativo_id):
    operativo = OperativoVehicular.objects.get(pk=operativo_id)
    form = SearchIndividuoForm()
    if request.method == 'POST':
        form = SearchIndividuoForm(request.POST)
        if form.is_valid():
            num_doc = form.cleaned_data['num_doc']
            try:
                individuo = Individuo.objects.get(num_doc=num_doc)
                operativo.cazadores.add(individuo)
                return redirect('seguimiento:ver_operativo', operativo_id=operativo.id)
            except Individuo.DoesNotExist:
                form.add_error(None, "No se ha encontrado a Nadie con esos Datos.")
    return render(request, "extras/generic_form.html", {'titulo': "Agregar Cazador", 'form': form, 'boton': "Agregar", })

@permission_required('operadores.operativos')
def quitar_cazador(request, operativo_id, individuo_id):
    operativo = OperativoVehicular.objects.get(pk=operativo_id)
    individuo = Individuo.objects.get(pk=individuo_id)
    operativo.cazadores.remove(individuo)
    return redirect('seguimiento:ver_operativo', operativo_id=operativo.id)

@permission_required('operadores.operativos')
def agregar_testeado(request, operativo_id):
    operativo = OperativoVehicular.objects.get(pk=operativo_id)
    form = SearchIndividuoForm()
    if request.method == 'POST':
        form = SearchIndividuoForm(request.POST)
        if form.is_valid():
            test = TestOperativo(operativo=operativo)
            test.num_doc = form.cleaned_data['num_doc']
            try:
                test.individuo = Individuo.objects.get(num_doc=test.num_doc)
            except Individuo.DoesNotExist:
                pass #Si no tenemos el dni no pasa naranja (Pedimos los otros datos despues)
            test.save()
            return redirect('seguimiento:ver_operativo', operativo_id=operativo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Agregar Testeado", 'form': form, 'boton': "Agregar", })

#@permission_required('operadores.operativos')
#def quitar_cazador(request, test_id):

#Otros listados
@permission_required('operadores.individuos')
def ranking_test(request):
    #Buscamos los que tenemos que analizar
    #individuos = obtener_bajo_seguimiento()
    individuos = Individuo.objects.filter(seguimientos__tipo='PT')
    #individuos = individuos.filter(seguimientos__tipo='PT')
    individuos = individuos.exclude(seguimientos__tipo__in=('ET','DT'))
    individuos = individuos.distinct()
    #Optimizamos
    individuos = individuos.select_related('situacion_actual')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__ubicacion')
    individuos = individuos.prefetch_related('seguimientos', 'patologias', 'atributos')
    #Rankeamos
    excepciones = [t[0] for t in TIPO_ATRIBUTO if len(t[0]) == 3]
    for individuo in individuos:
        individuo.pedido = [s for s in individuo.seguimientos.all() if s.tipo == 'PT'][-1]
        #1pt por cada dia despues del 4to
        dias = int((timezone.now() - individuo.situacion_actual.fecha).total_seconds() / 3600 / 24)
        individuo.puntaje = int((timezone.now() - individuo.situacion_actual.fecha).total_seconds() / 3600 / 24) - 4
        individuo.motivos = ["Dias: " + str(dias), ]
        #2 pts por cada atributo de excepcion
        atribs = [a.get_tipo_display() for a in individuo.atributos.all() if a.tipo in excepciones]
        if atribs:
            individuo.puntaje += len(atribs) * 2
            individuo.motivos += ["Excepciones:", ] + atribs
        #3 pts por cada patologia
        pats = [p.get_tipo_display() for p in individuo.patologias.all()]
        if pats:
            individuo.puntaje += len(pats) * 3
            individuo.motivos += ["Patologias:", ] + pats
        #+50 por Test Prioritario
        if individuo.atributos.filter(tipo='TP').exists():
            individuo.puntaje += 50
            individuo.motivos += ["Ranking Prioritario", ]
        #Ranking de puntajes:
    #Mostramos
    return render(request, "ranking_test.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def esperando_test(request):
    #Buscamos los que tenemos que analizar
    individuos = Individuo.objects.filter(seguimientos__tipo='ET')
    individuos = individuos.exclude(seguimientos__tipo__in=('DT','CT'))
    #optimizamos
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__ubicacion')
    individuos = individuos.prefetch_related('seguimientos')
    #Obtenemos el dato del test:
    for individuo in individuos:
        individuo.pedido_test = [et for et in individuo.seguimientos.all() if et.tipo=='ET'][-1]
    #Mostramos
    return render(request, "esperando_test.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def test_realizados(request):
    #Buscamos los que tenemos que analizar
    individuos = Individuo.objects.filter(seguimientos__tipo__in=('DT','CT'))
    #optimizamos
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__ubicacion')
    individuos = individuos.prefetch_related('seguimientos')
    #Obtenemos el dato del test:
    for individuo in individuos:
        individuo.test = [rt for rt in individuo.seguimientos.all() if rt.tipo in ('DT','CT')][-1]
    #Mostramos
    return render(request, "lista_testeados.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def lista_sin_telefono(request):
    individuos = Individuo.objects.filter(seguimientos__tipo='TE')
    individuos = individuos.filter(situacion_actual__conducta__in=('D', 'E'))
    #Optimizamos
    individuos = individuos.select_related('nacionalidad')
    individuos = individuos.select_related('situacion_actual', 'seguimiento_actual')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
    #Lanzamos reporte    
    return render(request, "lista_sin_telefonos.html", {
        'individuos': individuos,
        'has_table': True,
    })

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
    individuos = individuos.select_related('situacion_actual', 'seguimiento_actual')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
    individuos = individuos.select_related('appdata')
    individuos = individuos.prefetch_related('vigiladores', 'vigiladores__operador')
    #Lanzamos reporte
    return render(request, "lista_seguidos.html", {
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
