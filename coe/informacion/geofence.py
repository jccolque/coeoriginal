#Imports de Python
from datetime import timedelta
#Imports de Django
from django.utils import timezone
from django.core.cache import cache
#Imports Extras
from geographiclib.geodesic import Geodesic
#Imports del proyecto
from coe.constantes import LAST_DATETIME
#Imports de la app
from .models import GeoPosicion, Seguimiento, Permiso

#Definimos nuestras funciones:
def obtener_base(num_doc):
    geopos_bases = cache.get("geopos_bases")
    try:
        return geopos_bases[num_doc]
    except:
        try:
            gps = GeoPosicion.objects.get(
                    individuo__num_doc=num_doc,
                    tipo='ST')
            if not geopos_bases:#Creamos la base inicial
                geopos_bases = {g.individuo.num_doc: g for g in GeoPosicion.objects.filter(tipo='ST')}
            geopos_bases[num_doc] = gps
            cache.set("geopos_bases", geopos_bases)
            return geopos_bases[num_doc]
        except GeoPosicion.DoesNotExist:
            return None

def renovar_base(nueva_geopos):
    geopos_bases = cache.get("geopos_bases")
    if geopos_bases:
        geopos_bases[nueva_geopos.individuo.num_doc] = geopos_bases
        cache.set("geopos_bases", geopos_bases)

def controlar_distancia(nueva_geopos):
    #Obtenemos su posicion Permitida
    gps_base = obtener_base(nueva_geopos.individuo.num_doc)
    #Calculamos diferencia
    geodesic = Geodesic.WGS84.Inverse(gps_base.latitud, gps_base.longitud, nueva_geopos.latitud, nueva_geopos.longitud)
    distancia = geodesic['s12']# en metros
    if distancia > 50:#Si tiene mas de 50 metros
        seguimiento = Seguimiento()
        seguimiento.individuo = gps_base.individuo
        seguimiento.tipo = 'AT'
        seguimiento.aclaracion = 'Distancia: '+str(distancia)+'mts | '+str(nueva_geopos.fecha)
        seguimiento.save()
    return distancia

def buscar_permiso(individuo, activo=False):
    permisos = Permiso.objects.filter(individuo=individuo, endda__gt=timezone.now())
    if activo:#Chequear que este activo
        permisos = permisos.filter(begda__lt=timezone.now())
    permiso = permisos.first()
    if not permiso:
        #Chequeamos que el individuo no tenga atributo laboral para permiso permanente:
        atributos = individuo.atributos.filter(tipo__in=('AS','PS','FP','TE'))
        if atributos:
            atributo = atributos.first()
            permiso = Permiso()
            permiso.individuo = individuo
            permiso.tipo = 'P'
            permiso.localidad = individuo.domicilio_actual.localidad
            permiso.begda = timezone.now()
            permiso.endda = LAST_DATETIME
            permiso.aclaracion = "Permiso Permanente: " + atributo.get_tipo_display()
            permiso.save()
    return permiso

def validar_permiso(individuo, data):
    #Inicializamos permiso:
    permiso = Permiso()
    permiso.aprobar = True
    #REALIZAR TODA LA LOGICA
    #Chequeamos que no este en cuarentena obligatoria o aislado
    if individuo.situacion_actual.conducta in ('D', 'E'):
        permiso.aprobar = False
        permiso.aclaracion = "Usted se encuentra bajo " + individuo.situacion_actual.get_conducta_display() + " Por favor mantengase en su Hogar."
    else:
        #Chequeamos que no tenga un permiso hace menos de 3 dias (DEL MISMO TIPO?):
        cooldown = timezone.now() - timedelta(days=3)
        permisos = individuo.permisos.filter(endda__gt=cooldown, tipo=data["tipo_permiso"])
        if permisos:
            permiso.aprobar = False
            permiso.aclaracion = "Usted recibio un Permiso el dia " + str(permisos.last().endda.date())
        else:
            #Chequeamos que nadie del domicilio tenga permiso
            for relacion in individuo.relaciones.filter(tipo="MD"):
                if relacion.relacionado.permisos.filter(endda__gt=cooldown, tipo=data["tipo_permiso"]):
                    relacionado = relacion.relacionado
                    permiso.aprobar = False
                    permiso.aclaracion = relacionado.nombres + ' ' + relacionado.apellidos + ' Ya obtuvo un permiso en los ultimos dias.' 
    #Devolvemos todo lo procesado
    return permiso
    