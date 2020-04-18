#Imports de Python
from datetime import timedelta
#Imports de Django
from django.utils import timezone
from django.core.cache import cache
from django.http import JsonResponse
#Imports Extras
from geographiclib.geodesic import Geodesic
#Imports del proyecto
from coe.constantes import LAST_DATETIME
from coe.constantes import DISTANCIA_MAXIMA, CENTRO_LATITUD, CENTRO_LONGITUD
from informacion.models import Seguimiento
from permisos.models import Permiso
#Imports de la app
from .models import GeoPosicion

#Definimos nuestras funciones:
def obtener_base(num_doc):
    geopos_bases = cache.get("geopos_bases")
    #Si no tenemos la cache, la generamos de CERO
    if not geopos_bases:
        geopos_bases = GeoPosicion.objects.select_related('individuo', 'individuo__appdata')
        geopos_bases = geopos_bases.filter(tipo='PC')
        geopos_bases = {g.individuo.num_doc: g for g in geopos_bases}
        cache.set("geopos_bases", geopos_bases)
    #Ahora buscamos el de este:
    try:
        return geopos_bases[num_doc]
    except KeyError:
        gps = GeoPosicion.objects.select_related('individuo', 'individuo__appdata')
        #No tiene, hay que generar una nueva:
        try:
            gps = gps.get(individuo__num_doc=num_doc, tipo='PC')
            geopos_bases[num_doc] = gps
        except GeoPosicion.DoesNotExist:#Si no encontramos buscamos otra
            gps = None
        #Devolvemos
    return gps

def renovar_base(nueva_geopos):
    geopos_bases = cache.get("geopos_bases")
    if geopos_bases:
        geopos_bases[nueva_geopos.individuo.num_doc] = nueva_geopos
        cache.set("geopos_bases", geopos_bases)

def controlar_distancia(nueva_geopos):
    #Mensajes vacios
    nueva_geopos.notif_titulo = ""
    nueva_geopos.notif_mensaje = ""
    #Obtenemos su posicion Permitida
    gps_base = obtener_base(nueva_geopos.individuo.num_doc)
    if gps_base:
        appdata = gps_base.individuo.appdata
        #Calculamos diferencia
        geodesic = Geodesic.WGS84.Inverse(gps_base.latitud, gps_base.longitud, nueva_geopos.latitud, nueva_geopos.longitud)
        nueva_geopos.distancia = geodesic['s12']# en metros
        if nueva_geopos.distancia > appdata.distancia_alerta:#Si tiene mas de 50 metros
            nueva_geopos.alerta = 'DA'
            if nueva_geopos.distancia > appdata.distancia_alerta:
                nueva_geopos.alerta = 'DC'
            nueva_geopos.notif_titulo = "Covid19 - Alerta por Distancia"
            nueva_geopos.notif_mensaje = "Usted se ha alejado a "+str(int(nueva_geopos.distancia))+"mts del area permitida."
            #Cargamos registro de seguimiento
            seguimiento = Seguimiento()
            seguimiento.individuo = gps_base.individuo
            seguimiento.tipo = 'AT'
            seguimiento.aclaracion = 'Distancia: '+str(nueva_geopos.distancia)+'mts | '+str(nueva_geopos.fecha)
            seguimiento.save()
    else:
        nueva_geopos.alerta = 'SC'
    return nueva_geopos

def es_local(geopos):
    #Calculamos diferencia
    geodesic = Geodesic.WGS84.Inverse(CENTRO_LATITUD, CENTRO_LONGITUD, geopos.latitud, geopos.longitud)
    distancia = geodesic['s12']# en metros
    if distancia < DISTANCIA_MAXIMA:#Si esta dentro del radio aceptable
        return True

#Salvoconducos
def buscar_permiso(individuo, activo=False):
    permisos = Permiso.objects.filter(individuo=individuo, endda__gt=timezone.now())
    permisos = permisos.select_related('individuo', 'individuo__domicilio_actual')
    if activo:#Chequear que este activo
        permisos = permisos.filter(begda__lt=timezone.now())
    permiso = permisos.first()
    if not permiso:
        #Chequeamos que el individuo no tenga atributo laboral para permiso permanente:
        atributos = individuo.atributos.filter(tipo__in=('AS','PS','FP'))
        if atributos:
            atributo = atributos.first()
            permiso = Permiso()
            permiso.individuo = individuo
            permiso.tipo = 'P'
            permiso.localidad = individuo.domicilio_actual.localidad
            permiso.begda = timezone.now()
            permiso.endda = LAST_DATETIME
            permiso.aclaracion = "Permiso Permanente: " + atributo.get_tipo_display()
            permiso.control = True
            permiso.save()
    if permiso:
        permiso.aprobar = True
    return permiso

#Validamos la posibilidad de otorgar el permiso
def pedir_permiso(individuo, tipo_permiso, permiso=None):
    #Inicializamos permiso:
    if permiso:#Si encontro un permiso previamente guardado
        permiso.aprobar = True
    else:
        permiso = Permiso()
        permiso.aprobar = True
        permiso.localidad = individuo.domicilio_actual.localidad
        permiso.controlador = individuo.controlador_salvoconducto()
        #REALIZAR TODA LA LOGICA
        #Chequeamos que no este en cuarentena obligatoria o aislado
        if individuo.situacion_actual.conducta in ('D', 'E'):
            permiso.aprobar = False
            permiso.aclaracion = "Usted se encuentra bajo " + individuo.situacion_actual.get_conducta_display() + " Mantengase en su Hogar."
        else:
            #Chequeamos que no tenga un permiso hace menos de 3 dias
            cooldown = timezone.now() - timedelta(days=3)
            permisos = individuo.permisos.filter(endda__gt=cooldown)#, tipo=tipo_permiso)#(DEL MISMO TIPO?):
            if permisos:
                permiso.aprobar = False
                permiso.aclaracion = "Usted recibio un Permiso el dia " + str(permisos.last().endda.date())
            else:
                #Chequeamos que nadie del domicilio tenga permiso
                for relacion in individuo.relaciones.filter(tipo="MD"):
                    if relacion.relacionado.permisos.filter(endda__gt=cooldown, tipo=tipo_permiso):
                        relacionado = relacion.relacionado
                        permiso.aprobar = False
                        permiso.aclaracion = relacionado.nombres + ' ' + relacionado.apellidos + ' Ya obtuvo un permiso en los ultimos dias.' 
        #Devolvemos todo lo procesado
        #HARDCODEADO HASTA QUE SE APRUEBE:
        permiso.aprobar = False
        permiso.aclaracion = "Esta Funcionalidad aun no fue Aprobada. Sigue Vigente Permiso Nacional."
        #Funcionar
    return permiso

#Aca ordenamos por zonas y tiempos
def definir_fechas(permiso, fecha_ideal):
    #Agregar Control DNI por dias
    #Aca tenemos que poner los horarios de comercio/fabricas
    #Aca tenemos que poner controles por zona (Podriamos usar su ultima posicion gps conocida)
    permiso.begda = timezone.now() + timedelta(days=1)
    permiso.endda = timezone.now() + timedelta(days=1, hours=2)
    return permiso

def json_permiso(permiso, vista):
    return JsonResponse(
            {
                "action": vista,
                "realizado": True,
                "tipo_permiso": permiso.get_tipo_display(),
                "dni_individuo": permiso.individuo.num_doc,
                "nombre_completo": permiso.individuo.apellidos + ', ' + permiso.individuo.nombres,
                "domicilio": permiso.individuo.domicilio_actual.nombre_corto(),
                "fecha_inicio": permiso.begda.date(),
                "hora_inicio": permiso.begda.time(),
                "fecha_fin": permiso.endda.date(),
                "hora_fin": permiso.endda.time(),
                "imagen": permiso.individuo.get_foto(),
                "qr": permiso.individuo.get_qr(),
                "control": permiso.controlador,
                "texto": permiso.aclaracion,

            },
            safe=False
        )