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
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
#Imports extras
from auditlog.models import LogEntry
#Imports del proyecto
from coe.settings import GEOPOSITION_GOOGLE_MAPS_API_KEY
from coe.constantes import DIAS_CUARENTENA, NOTEL
from core.decoradores import superuser_required
from core.functions import date2str
from core.forms import SearchForm, JustificarForm, UploadCsv
from georef.models import Nacionalidad
from georef.models import Ubicacion
from graficos.functions import obtener_grafico
from operadores.models import Operador
from operadores.functions import obtener_operador
from informacion.choices import atributos_excepcionales, TIPO_PATOLOGIA
from informacion.models import Individuo, Atributo, Patologia
from informacion.models import SignosVitales, Relacion
from informacion.models import Situacion, Documento
from informacion.models import Vehiculo
from informacion.forms import ArchivoForm, SearchIndividuoForm, BuscarIndividuoSeguro
from geotracking.models import GeoPosicion
from operadores.functions import obtener_operador
from app.models import AppData, AppNotificacion
from app.functions import activar_tracking, desactivar_tracking
from background.functions import crear_progress_link
#imports de la app
from .choices import TIPO_VIGIA
from .models import Seguimiento, Vigia, HistVigilancias, Configuracion
from .models import OperativoVehicular, TestOperativo
from .models import Condicion
from .forms import SeguimientoForm
from .forms import NuevoVigia, ConfiguracionForm, NuevoIndividuo
from .forms import OperativoForm, TestOperativoForm
from .forms import CondicionForm, AtenderForm
from .functions import esperando_seguimiento, vigilancias_faltantes
from .functions import asignar_vigilante
from .functions import realizar_alta
from .tasks import altas_masivas, guardar_muestras_bg
#Agregados pablo
from .forms import DatosGisForm
from .models import DatosGis
from .models import Muestra
from .forms import BioqEditForm, PanelEditForm
from .forms import PriorForm

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
        'tipos_excepciones': atributos_excepcionales(),
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
    if seguimiento_id:
        seguimiento = Seguimiento.objects.get(pk=seguimiento_id)
        form = SeguimientoForm(instance=seguimiento, user=request.user)
    else:
        form = SeguimientoForm(initial={'tipo': tipo}, user=request.user)
    if request.method == "POST":
        form = SeguimientoForm(request.POST, instance=seguimiento, user=request.user)
        if form.is_valid():
            seguimiento = form.save(commit=False)
            seguimiento.individuo = Individuo.objects.get(pk=individuo_id)
            seguimiento.operador = obtener_operador(request)
            seguimiento.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Seguimiento", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def del_seguimiento(request, seguimiento_id=None):
    seguimiento = Seguimiento.objects.get(pk=seguimiento_id)
    individuo = seguimiento.individuo
    seguimiento.delete()
    return render(request, "extras/close.html")

#CONDICIONES
@permission_required('operadores.individuos')
def crear_condicion(request, individuo_id, condicion_id=None):
    #obtenemos individuo
    individuo = Individuo.objects.get(pk=individuo_id)
    #buscamos condicion PreExistente
    condicion = None
    if condicion_id:
        condicion = Condicion.objects.get(pk=condicion_id)
    #Creamos Form
    form = CondicionForm(instance=condicion)
    #Preguntamos si envio info:
    if request.method == "POST":
        form = CondicionForm(request.POST, instance=condicion)
        if form.is_valid():
            condicion = form.save(commit=False)
            condicion.individuo = individuo
            condicion.operador = obtener_operador(request)
            condicion.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Informar Condicion", 'form': form, 'boton': "Guardar", })

@permission_required('operadores.individuos')
def del_condicion(request, condicion_id=None):
    condicion = Condicion.objects.get(pk=condicion_id)
    individuo = condicion.individuo
    condicion.delete()
    return render(request, "extras/close.html")

#OPERACIONES
@permission_required('operadores.seguimiento')
def fin_seguimiento(request, vigia_id, individuo_id):
    #Obtenemos datos basicos
    vigia = Vigia.objects.get(pk=vigia_id)
    individuo = Individuo.objects.get(pk=individuo_id)
    #Generamos form
    form = SeguimientoForm(initial={'tipo': 'FS'}, user=request.user)
    if request.method == "POST":
        form = SeguimientoForm(request.POST, user=request.user)
        if form.is_valid():
            #Obtenemos seguimiento
            seg = form.save(commit=False)
            if not seg.tipo == "FS":
                return render(request, 'extras/error.html', {
                    'titulo': 'Esta opcion es solo para Finalizar Seguimientos',
                    'error': "Solo puede utilizarse con el tipo Final de Seguimiento.",
                })
            #Creamos FIN DE SEGUIMIENTO
            seg.individuo = individuo
            seg.operador = obtener_operador(request)
            Seguimiento.objects.bulk_create([seg, ])
            #Damos de baja el seguimiento    
            vigia.del_vigilado(individuo)
            return redirect('seguimiento:ver_panel', vigia_id=vigia_id)
    return render(request, "extras/generic_form.html", {'titulo': "Finalizar Seguimiento", 'form': form, 'boton': "Confirmar", })

#Listados
@permission_required('operadores.seguimiento_admin')
def reporte_vigilantes(request):
    #obtenemos vigilantes
    vigias = Vigia.objects.all()
    #Optimizamos
    vigias = vigias.select_related(
        'operador', 'operador__usuario',
        'configuracion'
    )
    vigias = vigias.prefetch_related(
        'operador__seguimientos_informados',
        'controlados',
        'controlados__seguimientos', 'controlados__seguimientos__operador',
    )
    #Preparamos filtros
    limite_1dia = timezone.now() - timedelta(hours=24)
    limite_2dias = timezone.now() - timedelta(hours=48)
    limite_3dias = timezone.now() - timedelta(hours=72)
    limite_semana = timezone.now() - timedelta(days=7)
    #Agregamos datos de interes:
    vigias = vigias.annotate(
            total_seguimientos=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(total_seguimientos=Count('seguimientos_informados')).values('total_seguimientos')[:1]
            ),
        ).annotate(
            seguimientos_semana=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(seguimientos_semana=Count('seguimientos_informados', filter=Q(seguimientos_informados__fecha__gt=limite_semana))).values('seguimientos_semana')[:1]
            ),
        ).annotate(
            seguimientos_3dias=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(seguimientos_3dias=Count('seguimientos_informados', filter=Q(seguimientos_informados__fecha__gt=limite_3dias))).values('seguimientos_3dias')[:1]
            ),
        ).annotate(
            seguimientos_2dias=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(seguimientos_2dias=Count('seguimientos_informados', filter=Q(seguimientos_informados__fecha__gt=limite_2dias))).values('seguimientos_2dias')[:1]
            ),
        ).annotate(
            seguimientos_1dia=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(seguimientos_1dia=Count('seguimientos_informados', filter=Q(seguimientos_informados__fecha__gt=limite_1dia))).values('seguimientos_1dia')[:1]
            ),
        ).annotate(
            altas_generadas=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(altas_generadas=Count('seguimientos_informados', filter=Q(seguimientos_informados__tipo='FS'))).values('altas_generadas')[:1]
            ),
    )    
    #Lanzamos reporte
    return render(request, "reporte_vigilantes.html", {
        'vigias': vigias,
        'has_table': True,
    })

@permission_required('operadores.seguimiento_admin')
def situacion_vigilancia(request):
    #obtenemos vigilantes
    vigias = Vigia.objects.all()
    #Optimizamos
    vigias = vigias.select_related(
        'operador', 'operador__usuario',
        'configuracion'
    )
    vigias = vigias.prefetch_related(
        'operador__seguimientos_informados',
        'controlados',
        'controlados__seguimientos', 'controlados__seguimientos__operador',
    )
    #Preparamos filtros
    limite_dia = timezone.now() - timedelta(hours=24)
    limite_semana = timezone.now() - timedelta(days=7)
    limite_2semanas = timezone.now() - timedelta(days=14)
    #generamos datos por tipo de vigilancia
    vigilancias = []
    #0-tipo 1-display 2-cant -3-activos -4 Controlados -5 mensajes_totales -6 mensajes_semanales
    for tipo in TIPO_VIGIA:
        tipo = [tipo[0], tipo[1], 0, 0, 0, 0, 0, 0, 0, 0]#Transformamos tupla en lista para operarla
        #Calculamos cantidad de vigilantes de ese tipo
        tipo[2] = sum([1 for v in vigias if v.tipo==tipo[0]])#Lo necesitamos para responsabilidad grupal
        #Cargamos controlados Actuales:
        for vigia in [v for v in vigias if v.tipo==tipo[0]]:
            #Activos: 3
            if vigia.activo:#Si esta activo
                tipo[3]+= 1
            #controlados 4
            tipo[4]+= sum([1 for c in vigia.controlados.all()])
            #max_controlados 5
            tipo[5]+= vigia.max_controlados
            #Disponibles 6
            tipo[6]+= vigia.cap_disponible()
            #Mensajes totales: 7
            tipo[7]+= sum([1 for s in vigia.operador.seguimientos_informados.all()])
            #Mensajes semanales: 8
            tipo[8]+= sum([1 for s in vigia.operador.seguimientos_informados.all() if s.fecha > limite_semana])
            #Responsabilidad Grupal
            if vigia.activo:
                responsabilidad = vigia.responsabilidad()
                if responsabilidad:#Si no es CERO
                    tipo[9]+= (responsabilidad / tipo[2])
        #Agregamos el tipo de vigilante
        vigilancias.append(tipo)
    #Generamos datos por vigilante:
    vigias = vigias.annotate(
            total_seguimientos=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(total_seguimientos=Count('seguimientos_informados')).values('total_seguimientos')[:1]
            ),
        ).annotate(
            semana_seguimientos=Subquery(
                Operador.objects.filter(pk=OuterRef('operador')).annotate(semana_seguimientos=Count('seguimientos_informados', filter=Q(seguimientos_informados__fecha__gt=limite_semana))).values('semana_seguimientos')[:1]
            ),
    )
    # #Generamos grafico
    # graf_vigilancia = obtener_grafico('graf_vigilancia', 'Grafico de Vigilancia', 'L')
    # graf_vigilancia.reiniciar_datos()
    # #Linea de Seguimientos
    # seguimientos = Seguimiento.objects.filter(fecha__gte=limite_2semanas).exclude(operador=None)
    # segs_dias = {}
    # for seguimiento in seguimientos:
    #     if seguimiento.fecha.date() in segs_dias:
    #         segs_dias[seguimiento.fecha.date()] += 1
    #     else:
    #         segs_dias[seguimiento.fecha.date()] = 1
    # for (fecha), cantidad in segs_dias.items():
    #     graf_vigilancia.bulk_dato(fecha, 'seguimientos', date2str(fecha), cantidad)
    # #Linea de Controlados
    # situaciones = Situacion.objects.filter(fecha__gte=limite_2semanas, fecha__lte=timezone.now(), conducta__in=('E','D'))
    # sits_dias = {}
    # for situacion in situaciones:
    #     if situacion.fecha.date() in sits_dias:
    #         sits_dias[situacion.fecha.date()] += 1
    #     else:
    #         sits_dias[situacion.fecha.date()] = 1
    # for fecha, cantidad in sits_dias.items():
    #     graf_vigilancia.bulk_dato(fecha, 'controlados', date2str(fecha), cantidad)
    # graf_vigilancia.bulk_save()
    # #Definimos algunos detalles del grafico:
    # graf_vigilancia.alto = 500
    #Lanzamos reporte
    return render(request, "situacion_vigilancia.html", {
        'vigilancias': vigilancias,
        'vigias': vigias,
        #'has_table': True,
        #'graf_vigilancia': graf_vigilancia,
    })

@permission_required('operadores.seguimiento')
def auditar_controlados(request, vigia_id=None):
    #Optimizamos
    vigilancias = HistVigilancias.objects.all()
    vigilancias = vigilancias.select_related(
        'vigia',
        'individuo', 'individuo__situacion_actual'
    )
    #Chequeamos si es para un vigia
    vigia = None
    if vigia_id:
        vigia = Vigia.objects.get(pk=vigia_id)
        vigilancias = vigilancias.filter(vigia=vigia)
    #Lanzamos reporte:
    return render(request, "auditoria_controlados.html", {
        'vigia': vigia,
        'vigilancias': vigilancias,
        'has_table': True,
    })

@permission_required('operadores.seguimiento_admin')
def seguimientos_vigia(request, vigia_id):
    vigia = Vigia.objects.all()
    #Optimizamos
    vigia = vigia.select_related('operador', 'operador__usuario')
    vigia = vigia.prefetch_related('controlados')
    vigia = vigia.prefetch_related('operador', 'operador__seguimientos_informados', 'operador__seguimientos_informados__individuo')
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
    individuos = Individuo.objects.exclude(vigiladores=None)
    #Optimizamos las busquedas
    individuos = individuos.select_related('nacionalidad')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
    individuos = individuos.select_related('situacion_actual', 'seguimiento_actual')
    individuos = individuos.prefetch_related('vigiladores', 'vigiladores__operador')
    #Obtenemos lista de vigilancias faltantes:
    individuos = vigilancias_faltantes(individuos)
    #Lanzamos reporte
    return render(request, "lista_seguidos.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.seguimiento_admin')
def carentes_seguimiento(request):
    #Obtenemos los vigilantes
    vigias = Vigia.objects.all()
    #Optimizamos:
    vigias = vigias.select_related(
        'operador', 'operador__usuario',
        'configuracion',
    )
    vigias = vigias.prefetch_related(
        'controlados',
        'controlados__seguimientos', 'controlados__seguimientos__operador',
        'controlados__situacion_actual',
    )
    #Preparamos lista para resultado:
    abandonados = []
    #Chequeamos a cada vigilante:
    vigias = list(vigias)#Lo transformamos en lista para poder meterle valores extra
    for vigia in vigias:
        config = vigia.get_config()#Obtenemos configuracion del vigia
        #Definimos limite para abandono (Alerta Amarilla):
        limite = timezone.now() - timedelta(hours=config.alerta_roja)#default: 36 horas
        #Chequeamos a todos los vigilados
        for individuo in vigia.controlados.all():
            llamadas = [l for l in individuo.seguimientos.all() if l.tipo == 'L' and l.operador == vigia.operador]
            if llamadas:#Si recibio llamadas pero son mas viejas que limite
                if llamadas[-1].fecha < limite:
                    individuo.llamada = llamadas[-1]
                    individuo.vigia = vigia
                    abandonados.append(individuo)
            else:
                individuo.vigia = vigia
                abandonados.append(individuo)
    #Lanzamos reportes
    return render(request, 'carentes_seguimiento.html', {
            'abandonados': abandonados,
            'has_table': True,
        }
    )

@permission_required('operadores.seguimiento')
def altas_cargadas(request, vigia_id=None):
    #Obtenemos altas realizadas
    altas = Seguimiento.objects.filter(tipo='FS')
    #Optimizamos
    altas = altas.select_related('individuo', 'individuo__situacion_actual')
    altas = altas.select_related('operador__vigia')
    #Filtramos si seleccion vigia
    vigia = None
    if vigia_id:
        vigia = Vigia.objects.get(pk=vigia_id)
        altas = altas.filter(operador=vigia.operador)
    #Lanzamos reportes
    return render(request, 'altas_cargadas.html', {
            'vigia': vigia,
            'altas': altas,
            'has_table': True,
        }
    )

#Administracion
@permission_required('operadores.seguimiento_admin')
def lista_sin_vigias(request):
    individuos = esperando_seguimiento()
    #Optimizamos las busquedas
    individuos = individuos.select_related('nacionalidad')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__ubicacion')
    individuos = individuos.select_related('situacion_actual', 'seguimiento_actual')
    individuos = individuos.prefetch_related('vigiladores', 'vigiladores__operador')
    #Obtenemos lista de vigilancias faltantes:
    individuos = vigilancias_faltantes(individuos)
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
            vigia.add_vigilado(individuo)
            return redirect('seguimiento:lista_sin_vigias')
    return render(request, "extras/generic_form.html", {'titulo': "Asignar Controlador", 'form': form, 'boton': "Asignar", })

@permission_required('operadores.seguimiento_admin')
def lista_vigias(request):
    vigias = Vigia.objects.all()
    vigias = vigias.select_related('operador', 'operador__usuario')
    vigias = vigias.select_related('configuracion')
    vigias = vigias.prefetch_related('controlados')
    #Obtenemos valor:
    limite = timezone.now() - timedelta(hours=18)
    seguimientos_actualizados = Seguimiento.objects.filter(tipo='L', fecha__gt=limite)#generamos subquery
    vigias = vigias.annotate(alertas=Count('controlados', exclude=Q(controlados__seguimiento__in=seguimientos_actualizados)))
    #Lanzamos listado
    return render(request, "lista_vigias.html", {
        'vigias': vigias,
        'has_table': True,
    })

@permission_required('operadores.seguimiento_admin')
def lista_ocupacion(request):
    vigias = Vigia.objects.all()
    vigias = vigias.select_related('operador', 'operador__usuario')
    vigias = vigias.prefetch_related('controlados', 'controlados__domicilio_actual', 'controlados__domicilio_actual__localidad')
    #Lanzamos listado
    return render(request, "lista_ocupacion.html", {
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
def configurar_vigia(request, vigia_id):
    vigia = Vigia.objects.get(pk=vigia_id)
    config = Vigia.get_config()
    form = ConfiguracionForm(instance=config)
    if request.method == "POST":
        form = ConfiguracionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            #Volvemos a la vista
            return redirect('seguimiento:ver_panel', vigia_id=config.vigia.id)
    #Lanzamos Form
    return render(request, "extras/generic_form.html", {'titulo': "Configurar Alertas", 'form': form, 'boton': "Configurar", })        

@permission_required('operadores.seguimiento')
def mod_estado_vigia(request, vigia_id):
    vigia = Vigia.objects.get(pk=vigia_id)
    vigia.activo = not vigia.activo#Invertimos estado
    vigia.save()
    return redirect('seguimiento:ver_panel', vigia_id=vigia_id)

@permission_required('operadores.seguimiento')
def rellenar_vigia(request, vigia_id):
    vigia = Vigia.objects.get(pk=vigia_id)
    #Buscamos todas las personas que requieran este tipo de seguimiento 
    limite = timezone.now() - timedelta(days=DIAS_CUARENTENA/2)#(1/2 cuarentena)
    pedido_actualizado = Atributo.objects.filter(tipo=vigia.tipo, fecha__gt=limite)
    individuos = Individuo.objects.filter(atributos__in=pedido_actualizado)
    #Que aun no tienen seguimiento de ese tipo
    individuos = individuos.exclude(vigiladores__tipo=vigia.tipo)
    #filtramos los que requieren seguimiento actualizado:
    individuos = esperando_seguimiento(individuos)
    #Si confirma
    if request.method == "POST":
        #asignamos hasta llenar el cupo
        for individuo in individuos:
            if vigia.controlados.count() < vigia.max_controlados:
                #Si aun hay lugar, lo agregamos
                vigia.add_vigilado(individuo)
            else:#Si ya no hay lugar, terminamos
                break
        #Volvemos al panel
        return redirect('seguimiento:ver_panel', vigia_id=vigia_id)
    #Mostramos el listado:
    return render(request, 'rellenar_vigia.html', {
            'vigia': vigia,
            'individuos': individuos[0:vigia.cap_disponible()],
            'has_form': True,
        }
    )


@permission_required('operadores.seguimiento_admin')
def del_vigia(request, vigia_id):
    vigia = Vigia.objects.get(pk=vigia_id)
    if request.method == "POST":
        #Guardamos la lista de controlados
        controlados = [c for c in vigia.controlados.all()]
        #Lo damos de baja:
        vigia.delete()
        #Asignamos todos sus controlados a otras personas
        for controlado in controlados:
            asignar_vigilante(controlado, vigia.tipo)
        #Volvemos a la lista de vigilancia
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
            #Obtenemos datos
            vigia = Vigia.objects.get(pk=vigia_id)
            individuo = form.cleaned_data['individuo']
            #Agregamos registro:
            atributo = Atributo(individuo=individuo)
            atributo.tipo = vigia.tipo
            atributo.aclaracion = "Seguimiento Manual cargado por " + str(obtener_operador(request))
            atributo.fecha = timezone.now()
            Atributo.objects.bulk_create([atributo, ])
            #Agregamos a vigilancia
            vigia.add_vigilado(individuo)
            #Volvemos a la vista
            return redirect('seguimiento:ver_panel', vigia_id=vigia.id)
    return render(request, "extras/generic_form.html", {'titulo': "Agregar Individuo Seguido", 'form': form, 'boton': "Agregar", })

@permission_required('operadores.seguimiento')
def quitar_vigilado(request, vigia_id, individuo_id):
    #Obtenemos vigia
    vigia = Vigia.objects.get(pk=vigia_id)
    #Obtenemos individuo a dar de baja
    individuo = Individuo.objects.get(pk=individuo_id)
    #Damos de baja
    vigia.del_vigilado(individuo)
    return redirect('seguimiento:ver_panel', vigia_id=vigia.id)

#Panel
@permission_required('operadores.seguimiento')
def panel_vigia(request, vigia_id=None):
    #Obtenemos el operador en cuestion
    vigias = Vigia.objects.select_related('operador', 'configuracion')
    vigias = vigias.prefetch_related(
        'controlados',
        'controlados__situacion_actual', 'controlados__atributos'
    )
    #Buscamos el vigia a mostrar
    if vigia_id:
        vigia = vigias.get(pk=vigia_id)
    else:
        operador = obtener_operador(request)
        try:
            vigia = vigias.get(operador=operador)
        except:
            return render(request, 'extras/error.html', {
            'titulo': 'No existe Panel de Vigilancia',
            'error': "Usted no es un Vigilante Habilitado, si deberia tener acceso a esta seccion, por favor contacte a los administradores.",
        })
    #Buscamos Alertas
    if vigia.tipo == "EM":#TODAS SON EMERGENCIAS YA!
        limite = timezone.now()
    else:
        config = vigia.get_config()
        limite = timezone.now() - timedelta(hours=config.alerta_verde)
    #Solo filtramos por el ultimo seguimiento tipo 'L'
    seguimiento_valido = Seguimiento.objects.filter(tipo='L', fecha__gt=limite, operador=vigia.operador)#generamos subquery
    individuos = vigia.controlados.exclude(seguimientos__in=seguimiento_valido)
    #Optimizamos
    individuos = individuos.select_related(
        'situacion_actual',
        'domicilio_actual', "domicilio_actual__localidad",
        'seguimiento_actual', 'seguimiento_actual__operador',
    )
    individuos = individuos.prefetch_related(
        'seguimientos', 'seguimientos__operador',
        'atributos',
        'condicion',
    )
    #Cargamos desde la ultima llamada de ese operador:
    individuos = list(individuos)
    for individuo in individuos:
        llamadas = [l for l in individuo.seguimientos.all() if l.tipo == 'L' and l.operador == vigia.operador]
        individuo.prioridad = 999
        if llamadas:
            individuo.prioridad = llamadas[-1].desde()
            individuo.desde_su_llamada = str(llamadas[-1].desde()) + "hrs"
        else:
            individuo.desde_su_llamada = "No registra"
    #Ordenamos por urgencia

    #Cargamos info a los controlados:
    lista_controlados = list(vigia.controlados.all())
    for controlado in lista_controlados:
        #Generamos la lista de fechas de inicio de seguimiento
        acciones = [h for h in controlado.vigilancias.all() if h.vigia==vigia and h.evento=="A"]
        if acciones:
             controlado.inicio = acciones[-1].fecha
        #Le cargamos la ultima llamada
        llamadas = [l for l in controlado.seguimientos.all() if l.operador==vigia.operador and l.tipo=="L"]
        if llamadas:
            controlado.llamada = llamadas[-1]
    #Lanzamos panel
    return render(request, "panel_vigia.html", {
        'vigia': vigia,
        'config': config,
        'individuos': individuos,
        'lista_controlados': lista_controlados,
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
        geoposiciones.append(operativo.get_geoposiciones().last())
    #Mostramos
    return render(request, "situacion_operativos.html", {
        'operativos': operativos,
        'geoposiciones': geoposiciones,
        'refresh': operativos.exists(),
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
        'has_table': True,
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

@permission_required('operadores.operativos')
def quitar_testeado(request, operativo_id, individuo_id):
    operativo = OperativoVehicular.objects.get(pk=operativo_id)
    individuo = Individuo.objects.get(pk=individuo_id)
    test = operativo.tests.filter(individuo=individuo).first()
    if test:
        test.delete()
    return redirect('seguimiento:ver_operativo', operativo_id=operativo.id)

#@permission_required('operadores.operativos')
#def quitar_cazador(request, test_id):

#Otros listados
@permission_required('operadores.individuos')
def ranking_test(request):
    #Buscamos los que tenemos que analizar
    individuos = Individuo.objects.filter(seguimientos__tipo='PT')
    #individuos = individuos.filter(seguimientos__tipo='PT')
    individuos = individuos.exclude(seguimientos__tipo__in=('ET','DT'))
    individuos = individuos.distinct()
    #Optimizamos
    individuos = individuos.select_related('situacion_actual')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__ubicacion')
    individuos = individuos.prefetch_related('seguimientos', 'patologias', 'atributos')
    #Rankeamos
    excepciones = atributos_excepcionales()
    for individuo in individuos:
        individuo.pedido = [s for s in individuo.seguimientos.all() if s.tipo == 'PT'][-1]
        #1pt por cada dia despues del 4to
        dias = int((timezone.now() - individuo.situacion_actual.fecha).total_seconds() / 3600 / 24)
        individuo.puntaje = int((timezone.now() - individuo.situacion_actual.fecha).total_seconds() / 3600 / 24) - 7
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
        #+100 sospechoso:
        if individuo.situacion_actual.estado == 40:
            individuo.puntaje += 75
            individuo.motivos += ["Sospechoso", ]
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
    individuos = individuos.prefetch_related('seguimientos')
    #Limpiamos duplicados
    individuos = individuos.distinct()
    #Generamos prioridad
    for individuo in individuos:
        pedido = [seg for seg in individuo.seguimientos.all() if seg.tipo == 'TE'][-1]
        individuo.prioridad = timezone.now() - pedido.fecha
        individuo.prioridad = individuo.prioridad.days
    #Lanzamos reporte
    return render(request, "lista_sin_telefonos.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def lista_requiere_atencion(request, atrib=None):
    #Obtenemos todas las condiciones que no fueron atendidas
    condiciones = Condicion.objects.filter(atendido=False)
    #Filtramos si es necesario:
    if atrib:
        condiciones = condiciones.filter(individuo__atributos__tipo=atrib)
    #Quitamos los que tienen menos de 20 puntos de prioridad
    
    #Quitamos los que fueron atendidos en territorio en las ultimas 24 horas
    limite = timezone.now() - timedelta(hours=24)
    atendido = Seguimiento.objects.filter(fecha__gt=limite, tipo="T")
    condiciones = condiciones.exclude(individuo__seguimientos__in=atendido)
    #optimizamos
    condiciones = condiciones.select_related(
        'individuo',
        'individuo__situacion_actual',
        'individuo__domicilio_actual', 'individuo__domicilio_actual__localidad',
        'operador',
    )
    condiciones = condiciones.prefetch_related(
        'individuo__seguimientos', 'individuo__seguimientos__operador',
    )
    #Lanzamos reporte
    return render(request, "lista_condiciones.html", {
        'condiciones': condiciones,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def atender_condiciones(request, condicion_id):
    #buscamos condicion PreExistente
    condicion = Condicion.objects.get(pk=condicion_id)
    #Creamos Form
    form = AtenderForm(instance=condicion)
    if request.method == "POST":#si envio info:
        form = AtenderForm(request.POST, instance=condicion)
        if form.is_valid():
            condicion = form.save(commit=False)
            condicion.operador = obtener_operador(request)
            condicion.atendido = not condicion.atendido
            condicion.save()
            return render(request, "extras/close.html")
    #Generamos titulo
    if condicion.atendido:
        titulo = "Negar informe de Atencion"
    else:
        titulo = "Informar Atencion Realizada/Eliminar Alerta"
    #lanzamos form
    return render(request, "extras/generic_form.html", {'titulo': titulo, 'form': form, 'boton': "Guardar", })

@permission_required('operadores.individuos')
def lista_atendidos(request):
    #Obtenemos todas las condiciones que no fueron atendidas
    condiciones = Condicion.objects.filter(atendido=True)
    #Quitamos los que tienen menos de 20 puntos de prioridad
    
    #optimizamos
    condiciones = condiciones.select_related(
        'individuo',
        'individuo__situacion_actual',
        'individuo__domicilio_actual', 'individuo__domicilio_actual__localidad',
        'operador',
    )
    #Lanzamos reporte
    return render(request, "lista_condiciones.html", {
        'condiciones': condiciones,
        'has_table': True,
    })

#Telefonico
@permission_required('operadores.individuos')
def quitar_lista_sintel(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    if request.method == "POST":
        #Le eliminamos la flag de telefono inexistente/errado
        individuo.seguimientos.filter(tipo='TE').delete()
        #Vemos si fue descartado de vigilancia por falta de telefono
        if individuo.telefono != NOTEL and not individuo.telefono:
            #Devolvemos todas las vigilancias no vencidas:
            limite = timezone.now() - timedelta(days=DIAS_CUARENTENA)
            tipos_de_vigia = [t[0] for t in TIPO_VIGIA]
            for vigilancia in individuo.atributos.filter(tipo__in=tipos_de_vigia, fecha__gt=limite):
                asignar_vigilante(individuo, vigilancia.tipo)
        #Volvemos a la lista
        return redirect('seguimiento:lista_sin_telefono')
    #Generamos Aviso:
    mensaje = "<b>Eliminara el Pedido de Telefono para:</b><br>"
    mensaje += "<b>" + str(individuo) + ".</b><br>"
    mensaje += "<b>Si realiza esta accion quedara registrada por su usuario.</b>"
    #Mostramos confirmacion:
    return render(request, "extras/confirmar.html", {
            'titulo': "Eliminar Seguimiento" + str(individuo),
            'message': mensaje,
            'has_form': True,
        }
    )

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
    #Obtenemos los datos:
    ultimo_aislamiento = individuo.situaciones.filter(conducta__in=('D','E')).last()
    if not ultimo_aislamiento:#Si no esta aislado por sistema pero lo estamos siguiendo
        ultimo_aislamiento = individuo.atributos.filter(tipo__in=('VE', 'ST', 'VT')).last()
    #Generamos datos
    inicio = ultimo_aislamiento.fecha
    fin = inicio + timedelta(days=DIAS_CUARENTENA)
    #Generamos Aviso:
    mensaje = "<b>Controle bien los siguientes datos:</b><br>"
    mensaje += "<b>Inicio:</b> " + str(inicio)[0:10] + " (Fecha ultima situacion de aislamiento)<br>"
    mensaje += "<b>Final:</b> " + str(fin)[0:10] + " (" +str(DIAS_CUARENTENA+1)+ " Dias Despues)<br><br>"
    mensaje += "<b>Si realiza esta accion quedara registrada por su usuario.</b>"
    #Mostramos confirmacion:
    return render(request, "extras/confirmar.html", {
            'titulo': "Dar de Alta a " + str(individuo),
            'message': mensaje,
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

#Sistema de muestras (TEST)

@permission_required('operadores.carga_gis')
def gis_list(request):
    datosgis = DatosGis.objects.all()   
    #Lanzamos listado
    return render(request, 'gis_list.html', {       
        'datosgis': datosgis,
        'has_table': True,
    })
    

@permission_required('operadores.carga_gis')
def cargar_gis(request, datosgis_id=None):
    datosgis = None    
    form = DatosGisForm()    
    if datosgis_id:
        datosgis = DatosGis.objects.get(pk=datosgis_id)
        form = DatosGisForm(instance=datosgis)        
    if request.method == 'POST':
        form = DatosGisForm(request.POST, instance=datosgis)
        if form.is_valid():
            datosgis = form.save(commit=False)            
            localidad = form.cleaned_data['localidad']
            datosgis.localidad = localidad
            datosgis.operador = obtener_operador(request)
            datosgis.save()
            return redirect('seguimiento:gis_list')
    return render(request, "carga_gis.html", {'form': form,})


class GisDel(LoginRequiredMixin, PermissionRequiredMixin, \
    SuccessMessageMixin, generic.DeleteView):
    permission_required = "operadores.carga_gis"  
    model=DatosGis
    template_name='delete_gis.html'
    context_object_name='obj'
    success_url=reverse_lazy("seguimiento:gis_list")
    success_message="Dato Epidemiológico Eliminado Satisfactoriamente"

#Sistema de muestras (TEST)
@permission_required('operadores.bioq_plp')
def muestra_list_bioq(request):
    muestras = Muestra.objects.all()
    muestras = muestras.select_related('operador')
    muestras = muestras.prefetch_related('individuo')
    return render(request, 'muestra_list_bioq.html',{
        'muestras': muestras,
        'has_table': True,
    })

@permission_required('operadores.panel_plp')
def muestra_list_panel(request):
    muestras = Muestra.objects.all()
    muestras = muestras.select_related('operador')
    muestras = muestras.prefetch_related('individuo')
    return render(request, 'muestra_list_panel.html',{
        'muestras': muestras,
        'has_table': True,
    })

@permission_required('operadores.carga_plp')
def muestra_list_comp(request):
    muestras = Muestra.objects.all()
    muestras = muestras.select_related('operador')
    muestras = muestras.prefetch_related('individuo')
    return render(request, 'muestra_list_comp.html',{
        'muestras': muestras,
        'has_table': True,
    })

@permission_required('operadores.carga_plp')
def buscar_persona_muestra(request):
    form = SearchIndividuoForm()
    if request.method == "POST":
        form = SearchIndividuoForm(request.POST)
        if form.is_valid():
            num_doc = form.cleaned_data['num_doc'].upper()
            try:
                individuo = Individuo.objects.get(num_doc=num_doc)
                return redirect('seguimiento:existe_plp', individuo_id=individuo.id, num_doc=num_doc)
            except Individuo.DoesNotExist:
                return redirect('seguimiento:cargar_muestra', num_doc=num_doc)
    return render(request, "extras/generic_form.html", {
        'titulo': "Indicar Documento de Individuo", 
        'form': form, 
        'boton': "Buscar", 
    })

@permission_required('operadores.carga_plp')
def cargar_muestra(request, individuo_id=None, num_doc=None):
    individuo = None
    form = PanelEditForm(initial={"num_doc":num_doc})     
    if individuo_id:
        individuo = Individuo.objects.get(pk=individuo_id, num_doc=num_doc)
        domicilio = individuo.domicilios.last()
        form = PanelEditForm(
            instance=individuo,
            initial={
                #Domicilio
                'dom_localidad': domicilio.localidad,               
                'dom_calle': domicilio.calle,
                'dom_numero': domicilio.numero,
                'dom_aclaracion': domicilio.aclaracion,             
            }
        )
    if request.method == "POST":
        form = PanelEditForm(request.POST, instance=individuo)       
        if form.is_valid():
            from informacion.functions import actualizar_individuo#evitamos dependencia circular
            individuo = actualizar_individuo(form)
            muestra = Muestra()
            muestra.numero = form.cleaned_data['numero']
            muestra.estado = form.cleaned_data['estado']
            muestra.prioridad = form.cleaned_data['prioridad']
            muestra.resultado = form.cleaned_data['resultado']
            muestra.fecha_muestra = form.cleaned_data['fecha_muestra']
            muestra.lugar_carga = form.cleaned_data['lugar_carga']
            muestra.grupo_etereo = form.cleaned_data['grupo_etereo']
            muestra.edad = form.cleaned_data['edad']
            muestra.operador = obtener_operador(request)               
            muestra.individuo = individuo
            muestra.save()
            return redirect('seguimiento:muestra_list_comp')
    return render(request, "extras/generic_form.html", {
        'titulo': "CARGA DE DATOS PLP",
        'form': form,
        'boton': "CARGAR DATOS",
    })


@permission_required('operadores.bioq_plp')
def edit_bioq(request, muestra_id):
    muestra = None
    form = BioqEditForm()
    if muestra_id:
        muestra = Muestra.objects.get(pk=muestra_id)
        form = BioqEditForm(instance=muestra)
    if request.method == 'POST':
        form = BioqEditForm(request.POST, request.FILES, instance=muestra)
        if form.is_valid():
            muestra = form.save(commit=False)
            muestra.operador = obtener_operador(request)
            muestra.save()
            return redirect('seguimiento:muestra_list_bioq')
    return render(request, "extras/generic_form.html", {
        'titulo': 'SUBIR RESULTADOS',
        'form': form,
        'boton': 'EDITAR',
    })

@permission_required('operadores.panel_plp')
def edit_panel(request, muestra_id=None):
    muestra = None    
    form = PriorForm()    
    if muestra_id:
        muestra = Muestra.objects.get(pk=muestra_id)
        form = PriorForm(instance=muestra)        
    if request.method == 'POST':
        form = PriorForm(request.POST, instance=muestra)
        if form.is_valid():
            muestra = form.save(commit=False)   
            muestra.operador = obtener_operador(request)
            muestra.save()
            return redirect('seguimiento:muestra_list_panel')
    return render(request, "extras/generic_form.html", {
        'titulo': 'EDITAR PRIORIDAD',
        'form': form,
        'boton': 'CAMBIAR PRIORIDAD'
        })

@permission_required('operadores.panel_plp')
def editar_muestra(request, muestra_id=None):
    muestra = Muestra.objects.get(pk=muestra_id)
    individuo = muestra.individuo
    domicilio = individuo.domicilios.last()
    form = PanelEditForm(
            instance=individuo,
            initial={
                #Domicilio
                'dom_localidad': domicilio.localidad,               
                'dom_calle': domicilio.calle,
                'dom_numero': domicilio.numero,
                'dom_aclaracion': domicilio.aclaracion,
                #Muestra                
                'estado': muestra.estado,
                'prioridad': muestra.prioridad,
                'resultado': muestra.resultado,
                'fecha_muestra': muestra.fecha_muestra,
                'lugar_carga': muestra.lugar_carga,
                'grupo_etereo': muestra.grupo_etereo,
                'edad': muestra.edad,
            }
        ) 
    if request.method == "POST":
        form = PanelEditForm(
            request.POST,
            instance=individuo,          
        )                  
        if form.is_valid():
            from informacion.functions import actualizar_individuo#evitamos dependencia circular
            individuo = actualizar_individuo(form)                
            muestra.estado = form.cleaned_data['estado']
            muestra.prioridad = form.cleaned_data['prioridad']
            muestra.resultado = form.cleaned_data['resultado']
            muestra.fecha_muestra = form.cleaned_data['fecha_muestra']
            muestra.lugar_carga = form.cleaned_data['lugar_carga']
            muestra.grupo_etereo = form.cleaned_data['grupo_etereo']
            muestra.edad = form.cleaned_data['edad']
            muestra.operador = obtener_operador(request)               
            muestra.save()
            return redirect('seguimiento:muestra_list_comp')
    return render(request, "extras/generic_form.html", {
        'titulo': "CARGA DE DATOS PLP",
        'form': form,
        'boton': "CARGAR DATOS",
    })

class MuestraDel(LoginRequiredMixin, PermissionRequiredMixin, \
    SuccessMessageMixin, generic.DeleteView):
    permission_required = "operadores.carga_plp"  
    model=Muestra
    template_name='delete_muestra.html'
    context_object_name='muestra'
    success_url=reverse_lazy("seguimiento:muestra_list_comp")
    success_message="Muestra Eliminada Satisfactoriamente"

@permission_required('operadores.carga_plp')
def upload_muestra(request):
    form = ArchivoForm(initial={'tipo':6, 'nombre': 'cargar_muestras_plp'+str(timezone.now())[0:16]})
    if request.method == "POST":
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo            
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            tarea = crear_progress_link(str(operador)+":cargar_muestras_plp("+str(timezone.now())[0:16].replace(' ','')+")")            
            #Dividimos en fragmentos
            frag_size = 500
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:#Procesamos todos menos el ultimo
                guardar_muestras_bg(segmento, archivo_id=archivo.id, queue=tarea)
            guardar_muestras_bg(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)                      
    return render(request, "extras/generic_form.html", {
        'titulo': "CARGA MASIVA DE MUESTRAS CSV", 
        'form': form, 
        'boton': "CARGAR ARCHIVO", 
    })