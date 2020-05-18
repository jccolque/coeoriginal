#Imports de Python
from datetime import timedelta
#Imports de Django
from django.core.cache import cache
#Imports Extras
from geographiclib.geodesic import Geodesic
#Imports del proyecto
from coe.constantes import DISTANCIA_MAXIMA, CENTRO_LATITUD, CENTRO_LONGITUD
from informacion.models import Individuo
from seguimiento.models import Seguimiento
#Imports de la app
from .models import GeoPosicion

#Definimos nuestras funciones:
def obtener_trackeados():
    individuos = Individuo.objects.filter(geoposiciones__tipo='ST')
    #Eliminamos los que terminaron el tracking:
    individuos = individuos.exclude(seguimientos__tipo='FT')
    #Optimizamos
    individuos = individuos.select_related('situacion_actual', 'domicilio_actual')
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'situacion_actual')
    individuos = individuos.prefetch_related('geoposiciones', 'geoperadores')
    #Nos quedamos solo con los que estan en Cuarentena o Aislamiento
    individuos = individuos.filter(situacion_actual__conducta__in=('D', 'E'))
    #Entregamos ese listado de Individuos
    return individuos

def obtener_base(num_doc):
    geopos_bases = cache.get("geopos_bases")
    #Si no tenemos la cache, la generamos de CERO
    if not geopos_bases:#Creamos la cache completa de bases si no existe
        #Traemos solo los que siguen bajo seguimiento
        individuos = obtener_trackeados()
        geopos_bases = GeoPosicion.objects.filter(individuo__in=individuos)
        geopos_bases = geopos_bases.filter(tipo='PC')
        #Optimizamos
        geopos_bases = geopos_bases.select_related('individuo', 'individuo__appdata')
        #Lo transformamos en diccionario
        geopos_bases = {g.individuo.num_doc:g for g in geopos_bases}
        #Seteamos cache
        cache.set("geopos_bases", geopos_bases)
    #Nos aseguramos de que este este actualizado
    if num_doc not in geopos_bases or not geopos_bases[num_doc]:
        geopos_bases[num_doc] = GeoPosicion.objects.filter(individuo__num_doc=num_doc, tipo='PC').last()
        cache.set("geopos_bases", geopos_bases)#Agregamos la busqueda
    #Ahora buscamos el de este:
    return geopos_bases[num_doc]

def obtener_repeticiones(geopos):
    geopos_movs = cache.get("geopos_movs")
    #Si no existe cache la iniciamos
    if not geopos_movs:
        geopos_movs = {}
    #Si no tenemos la cache, la generamos de CERO
    individuo = geopos.individuo
    if not individuo.num_doc in geopos_movs:
        geopos_movs[individuo.num_doc] = [geopos.latitud, geopos.longitud, 0]
    else:
        movs = geopos_movs[individuo.num_doc]
        if geopos.latitud == movs[0] and  geopos.longitud == movs[1]:
            geopos_movs[individuo.num_doc][2] += 1
        else:#Si cambio reseteamos
            geopos_movs[individuo.num_doc] = [geopos.latitud, geopos.longitud, 0]
    #Guardamos los cambios
    cache.set("geopos_movs", geopos_movs)
    #Devolvemos
    return geopos_movs[individuo.num_doc][2]

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

def control_movimiento(nueva_geopos):
    cant = obtener_repeticiones(nueva_geopos)
    #Chequeamos que se haya movido
    if cant > 6:#Mas de una hora sin mover el celular
        nueva_geopos.alerta = 'SM'
        nueva_geopos.aclaracion = 'Lleva ' + str(cant * 10) + 'mins sin registrar movimientos.'
    #Evitamos control a la hora de dormir
    return nueva_geopos