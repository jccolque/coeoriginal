#Imports de Python
#Imports de Django
from django.core.cache import cache
#Imports Extras
from geographiclib.geodesic import Geodesic
#Imports del proyecto
from coe.constantes import DISTANCIA_MAXIMA, CENTRO_LATITUD, CENTRO_LONGITUD
from informacion.models import Seguimiento
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