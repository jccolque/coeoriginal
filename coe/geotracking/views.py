#Imports Django
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from coe.settings import GEOPOSITION_GOOGLE_MAPS_API_KEY
from operadores.functions import obtener_operador
from core.forms import JustificarForm
from informacion.models import Individuo
#imports de la app
from .models import GeoPosicion, GeOperador
from .geofence import renovar_base
from .forms import ConfigGeoForm, NuevoGeoOperador, NuevoIndividuo, AsignarGeOperador

#Administrar
@permission_required('operadores.geotracking')
def menu_geotracking(request):
    try:
        es_geoperador = GeOperador.objects.get(operador__usuario=request.user)
    except:
        es_geoperador = False
    return render(request, 'menu_geotracking.html', {'es_geoperador': es_geoperador, })

#Tracking
@permission_required('operadores.geotracking_admin')
def control_tracking(request):
    #Obtenemos Alertas
    alertas = GeoPosicion.objects.exclude(alerta='SA').filter(procesada=False)
    alertas = alertas.select_related(
        'individuo', 'individuo__situacion_actual',
        'individuo__domicilio_actual', "individuo__domicilio_actual__localidad"
    )
    #Solo la ultima de cada uno
    dict_alertas = {alerta.individuo.num_doc:alerta for alerta in alertas}
    alertas = list(dict_alertas.values())
    #Lanzamos monitoreo
    return render(request, "control_tracking.html", {
        'gmkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
        'alertas': alertas,
        'has_table': True,
    })

@permission_required('operadores.geotracking_admin')
def lista_geooperadores(request):
    #Obtenemos el operador en cuestion
    geoperadores = GeOperador.objects.all()
    geoperadores = geoperadores.select_related('operador', 'operador__usuario')
    geoperadores = geoperadores.prefetch_related('controlados')
    return render(request, "lista_geoperadores.html", {
        'geoperadores': geoperadores,
        'has_table': True,
    })

@permission_required('operadores.geotracking')
def panel_geoperador(request, geoperador_id=None):
    #Obtenemos el operador en cuestion
    if geoperador_id:
        geoperador = GeOperador.objects.get(pk=geoperador_id)
    else:
        operador = obtener_operador(request)
        try:
            geoperador = operador.geoperador
        except:
            return render(request, 'extras/error.html', {
            'titulo': 'No existe Panel de GeOperador',
            'error': "Usted no es un GeOperador Habilitado, si deberia tener acceso a esta seccion, por favor contacte a los administradores.",
        })
    #Buscamos Alertas
    alertas = GeoPosicion.objects.exclude(alerta='SA').filter(procesada=False)
    alertas = alertas.filter(individuo__geoperador=geoperador)
    #Optimizamos
    alertas = alertas.select_related(
        'individuo', 'individuo__situacion_actual',
        'individuo__domicilio_actual', "individuo__domicilio_actual__localidad"
    )
    #Dejamos una sola por individuo
    dict_alertas = {alerta.individuo.num_doc:alerta for alerta in alertas}
    alertas = list(dict_alertas.values())
    #Lanzamos panel
    return render(request, "panel_geoperador.html", {
        'geoperador': geoperador,
        'alertas': alertas,
        'has_table': True,
    })

#Administracion
@permission_required('operadores.geotracking_admin')
def agregar_geoperador(request):
    form = NuevoGeoOperador()
    if request.method == "POST":
        form = NuevoGeoOperador(request.POST)
        if form.is_valid():
            form.save()
            return redirect('geotracking:lista_geooperadores')
    return render(request, "extras/generic_form.html", {'titulo': "Habilitar Nuevo GeoPerador", 'form': form, 'boton': "Habilitar", })

@permission_required('operadores.geotracking_admin')
def agregar_individuo(request, geoperador_id):
    form = NuevoIndividuo()
    if request.method == "POST":
        form = NuevoIndividuo(request.POST)
        if form.is_valid():
            geoperador = GeOperador.objects.get(pk=geoperador_id)
            individuo = form.cleaned_data['individuo']
            geoperador.controlados.add(individuo)
            return redirect('geotracking:ver_geopanel', geoperador_id=geoperador.id)
    return render(request, "extras/generic_form.html", {'titulo': "Agregar Individuo Seguido", 'form': form, 'boton': "Agregar", })         

#Listas
@permission_required('operadores.geotracking_admin')
def lista_sin_geoperador(request):
    #Obtenemos todos los que ya estan siendo controlados
    controlados = set()
    for geop in GeOperador.objects.all().prefetch_related('controlados'):
        for controlado in geop.controlados.all():
            controlados.add(controlado)
    #Sacamos los que no estan siendo trackeados
    geopos = GeoPosicion.objects.filter(tipo="ST").values_list("individuo__id", flat=True).distinct()
    geopos = geopos.exclude(individuo__in=controlados)
    #Obtenemos individuos de interes
    individuos = Individuo.objects.filter(id__in=geopos).select_related('situacion_actual', 'domicilio_actual')
    #Optimizamos
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'situacion_actual')
    individuos = individuos.prefetch_related('geoposiciones')
    return render(request, "lista_trackeados.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.geotracking_admin')
def asignar_geoperador(request, individuo_id):
    form = AsignarGeOperador()
    if request.method == "POST":
        form = AsignarGeOperador(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            geoperador = form.cleaned_data['geoperador']
            geoperador.controlados.add(individuo)
            return redirect('geotracking:lista_sin_geoperador')
    return render(request, "extras/generic_form.html", {'titulo': "Asignar Controlador", 'form': form, 'boton': "Asignar", })   

@permission_required('operadores.geotracking_admin')
def lista_trackeados(request):
    geopos = GeoPosicion.objects.filter(tipo="ST").values_list("individuo__id", flat=True).distinct()
    #Obtenemos individuos de interes
    individuos = Individuo.objects.filter(id__in=geopos).select_related('situacion_actual', 'domicilio_actual')
    #Optimizamos
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'situacion_actual')
    individuos = individuos.prefetch_related('geoposiciones')
    return render(request, "lista_trackeados.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.geotracking_admin')
def lista_alertas(request):
    #Obtenemos Alertas
    alertas = GeoPosicion.objects.filter(procesada=False).exclude(alerta='SA').exclude(alerta='FP')
    alertas = alertas.select_related(
        'individuo', 'individuo__situacion_actual',
        'individuo__domicilio_actual', "individuo__domicilio_actual__localidad"
    )
    alertas = alertas.order_by('distancia')
    dict_alertas = {alerta.individuo.num_doc:alerta for alerta in alertas}
    alertas = list(dict_alertas.values())
    #Lanzamos listado
    return render(request, "lista_alertas.html", {
        'alertas': alertas,
        'refresh': True,
        'has_table': True,
    })

@permission_required('operadores.geotracking_admin')
def alertas_procesadas(request):
    #Obtenemos Alertas
    alertas = GeoPosicion.objects.filter(procesada=True)
    alertas = alertas.select_related(
        'individuo', 'individuo__situacion_actual',
        'individuo__domicilio_actual', 'individuo__domicilio_actual__localidad',
        'operador',
    )
    dict_alertas = {alerta.individuo.num_doc:alerta for alerta in alertas}
    alertas = list(dict_alertas.values())
    #Lanzamos listado
    return render(request, "lista_procesadas.html", {
        'alertas': alertas,
        'refresh': True,
        'has_table': True,
    })

@permission_required('operadores.geotracking')
def ver_tracking(request, individuo_id):
    individuo = Individuo.objects.select_related('situacion_actual', 'domicilio_actual', 'appdata')
    individuo = individuo.get(pk=individuo_id)
    geoposiciones = GeoPosicion.objects.filter(individuo=individuo)
    geoposiciones = geoposiciones.select_related('individuo')
    geoposiciones = geoposiciones.order_by('-fecha')
    return render(request, "seguimiento.html", {
        'gmkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
        'individuo': individuo,
        'geoposiciones': geoposiciones,
    })

@permission_required('operadores.geotracking')
def procesar_alerta(request, geoposicion_id):
    geoposicion = GeoPosicion.objects.get(pk=geoposicion_id)
    form = JustificarForm(initial={'justificacion':geoposicion.aclaracion})
    if request.method == "POST":
        form = JustificarForm(request.POST)
        if form.is_valid:
            geoposicion.procesada = True
            geoposicion.operador = obtener_operador(request)
            geoposicion.aclaracion = request.POST['justificacion'] + '(' + str(geoposicion.operador) + ')'
            geoposicion.save()
            #Damos de baja el resto de las alertas
            GeoPosicion.objects.filter(
                individuo=geoposicion.individuo,
                procesada=False
            ).exclude(
                alerta='SA',
            ).update(
                procesada=True,
                operador=geoposicion.operador,
                aclaracion='Se proceso Alerta: '+str(geoposicion.id)+'. Justificativo: '+geoposicion.aclaracion
            )
            return redirect('geotracking:lista_alertas')
    return render(request, "extras/generic_form.html", {'titulo': "Procesar Alerta", 'form': form, 'boton': "Procesar", })

@permission_required('operadores.geotracking')
def cambiar_base(request, geoposicion_id):
    #Obtenemos la nueva base:
    geopos = GeoPosicion.objects.select_related('individuo').get(pk=geoposicion_id)
    operador = obtener_operador(request)
    #Desactivamos la anterior
    GeoPosicion.objects.filter(individuo=geopos.individuo, tipo='PC').update(tipo='RG', aclaracion="Desactivada: "+str(operador))
    #Desactivamos todas las alarmas
    GeoPosicion.objects.filter(individuo=geopos.individuo).update(alerta='SA', aclaracion="Desactivada por Cambio de Punto de Control.")
    #Generamos nuevo inicio Tracking
    geopos.tipo = 'PC'
    geopos.operador = operador
    geopos.aclaracion = "PUNTO DE CONTROL - Definido por:" + str(operador)
    geopos.save()
    #Renovamos cache para proximos checks
    renovar_base(geopos)
    #Volvemos al mapa
    return redirect('geotracking:ver_tracking', individuo_id=geopos.individuo.id)

@permission_required('operadores.geotracking')
def config_tracking(request, individuo_id):
    individuo = Individuo.objects.select_related('appdata').get(pk=individuo_id)
    appdata = individuo.appdata
    form = ConfigGeoForm(initial={
        'intervalo': appdata.intervalo,
        'distancia_alerta': appdata.distancia_alerta,
        'distancia_critica': appdata.distancia_critica,
    })
    if request.method == "POST":
        form = ConfigGeoForm(request.POST)
        if form.is_valid():
            appdata.intervalo = form.cleaned_data["intervalo"]
            appdata.distancia_alerta = form.cleaned_data["distancia_alerta"]
            appdata.distancia_critica = form.cleaned_data["distancia_critica"]
            appdata.save()
            return redirect('geotracking:ver_tracking', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Configurar Parametros Individuales", 'form': form, 'boton': "Configurar", })