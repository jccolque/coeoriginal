#Imports Django
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from coe.settings import GEOPOSITION_GOOGLE_MAPS_API_KEY
from operadores.functions import obtener_operador
from core.forms import JustificarForm
#imports de la app
from .models import Individuo
from .models import GeoPosicion
from .geofence import renovar_base
from .geo_forms import ConfigGeoForm

#Administrar
@permission_required('operadores.geotracking')
def menu_geotracking(request):
    return render(request, 'geotracking/menu_geotracking.html', {})

#Tracking
@permission_required('operadores.geotracking')
def control_tracking(request):
    #Obtenemos Posiciones Bases
    geoposiciones = GeoPosicion.objects.filter(tipo='PC')
    #Obtenemos Alertas
    alertas = GeoPosicion.objects.exclude(alerta=None).filter(procesada=False)
    alertas = alertas.select_related(
        'individuo', 'individuo__situacion_actual',
        'individuo__domicilio_actual', "individuo__domicilio_actual__localidad"
    )
    #Solo la ultima de cada uno
    dict_alertas = {alerta.individuo.num_doc:alerta for alerta in alertas}
    alertas = list(dict_alertas.values())
    #Lanzamos monitoreo
    return render(request, "geotracking/control_tracking.html", {
        'gmkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
        'geoposiciones': geoposiciones,
        'alertas': alertas,
        'has_table': True,
    })

@permission_required('operadores.geotracking')
def lista_trackeados(request):
    geopos = GeoPosicion.objects.all().values_list("individuo__id", flat=True).distinct()
    #Obtenemos individuos de interes
    individuos = Individuo.objects.filter(id__in=geopos).select_related('situacion_actual', 'domicilio_actual')
    #Optimizamos
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'situacion_actual')
    individuos = individuos.prefetch_related('geoposiciones')
    return render(request, "geotracking/lista_trackeados.html", {
        'individuos': individuos,
        'has_table': True,
    })

@permission_required('operadores.geotracking')
def lista_alertas(request):
    #Obtenemos Alertas
    alertas = GeoPosicion.objects.filter(procesada=False).exclude(alerta=None).exclude(alerta='FP')
    alertas = alertas.select_related(
        'individuo', 'individuo__situacion_actual',
        'individuo__domicilio_actual', "individuo__domicilio_actual__localidad"
    )
    alertas = alertas.order_by('distancia')
    dict_alertas = {alerta.individuo.num_doc:alerta for alerta in alertas}
    alertas = list(dict_alertas.values())
    #Lanzamos listado
    return render(request, "geotracking/lista_alertas.html", {
        'alertas': alertas,
        'refresh': True,
        'has_table': True,
    })

@permission_required('operadores.geotracking')
def alertas_procesadas(request):
    #Obtenemos Alertas
    alertas = GeoPosicion.objects.filter(procesada=True)
    alertas = alertas.select_related(
        'individuo', 'individuo__situacion_actual',
        'individuo__domicilio_actual', 'individuo__domicilio_actual__localidad',
        'operador',
    )
    alertas = alertas.order_by('-fecha')
    #Lanzamos listado
    return render(request, "geotracking/lista_procesadas.html", {
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
    return render(request, "geotracking/seguimiento.html", {
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
            GeoPosicion.objects.filter(
                individuo=geoposicion.individuo,
                procesada=False
            ).exclude(
                alerta=None,
            ).update(
                procesada=True,
                operador=geoposicion.operador,
                aclaracion='Se proceso Alerta: '+str(geoposicion.id)+'.Justificativo: '+geoposicion.aclaracion
            )
            return redirect('geo_urls:lista_alertas')
    return render(request, "extras/generic_form.html", {'titulo': "Procesar Alerta", 'form': form, 'boton': "Procesar", })

@permission_required('operadores.geotracking')
def cambiar_base(request, geoposicion_id):
    #Obtenemos la nueva base:
    geopos = GeoPosicion.objects.select_related('individuo').get(pk=geoposicion_id)
    #Desactivamos la anterior
    GeoPosicion.objects.filter(individuo=geopos.individuo, tipo='PC').update(tipo='RG', aclaracion="Desactivada: "+str(obtener_operador(request)))
    #Desactivamos todas las alarmas previas a esta alarma
    GeoPosicion.objects.filter(individuo=geopos.individuo).update(alerta=None, aclaracion="Desactivada por Cambio de Punto de Control.")
    #Generamos nuevo inicio Tracking
    geopos.tipo = 'PC'
    geopos.aclaracion = "PUNTO DE CONTROL - Definido por:" + str(obtener_operador(request))
    geopos.save()
    #Renovamos cache para proximos checks
    renovar_base(geopos)
    #Volvemos al mapa
    return redirect('geo_urls:ver_tracking', individuo_id=geopos.individuo.id)

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
            return redirect('geo_urls:ver_tracking', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Configurar Parametros Individuales", 'form': form, 'boton': "Configurar", })