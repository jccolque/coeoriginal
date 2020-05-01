#Imports de Python
import logging
import traceback
from datetime import timedelta
#Imports django
from django.utils import timezone
#Imports Extras
from background_task import background
#Imports del proyeco
from coe.constantes import DIAS_CUARENTENA
from informacion.models import Seguimiento
from app.models import AppNotificacion
#Import de la app
from .models import GeoPosicion
from .geofence import obtener_trackeados

#Definimos logger
logger = logging.getLogger("tasks")

#Definimos tareas
@background(schedule=1)
def geotrack_sin_actualizacion():
    logger.info("GeoTrackings Sin actualizar")
    individuos = obtener_trackeados()
    #Quitamos los que enviaron Posicion GPS en las ultimas 2 horas:
    limite = timezone.now() - timedelta(hours=2)
    individuos = individuos.exclude(geoposiciones__in=GeoPosicion.objects.filter(fecha__gt=limite, tipo='RG'))
    #Quitamos los que ya fueron infomados
    #individuos = individuos.exclude(Q(geoposiciones__alerta='FG', geoposiciones__procesada=True))
    #Recorrer y alertar
    for individuo in individuos:
        logger.info("Procesamos: " + str(individuo))
        try:
            geopos = individuo.geoposiciones.last()
            geopos.alerta = 'FG'
            geopos.procesada = False
            horas = int((geopos.fecha - timezone.now()).seconds / 3600)
            geopos.aclaracion = "Lleva " + str(horas) + "hrs sin informar posicion."
            geopos.save()
            #eliminamos si tiene una notificacion esperando
            AppNotificacion.objects.filter(appdata=individuo.appdata).delete()
            #Creamos nueva Notificacion
            try:
                notif = AppNotificacion()
                notif.appdata = individuo.appdata
                notif.titulo = 'Falta de Seguimiento'
                notif.mensaje = 'Hace mas de ' + str(horas) + ' que no recibimos su posicion.'
                notif.accion = 'SL'
                notif.save()#Al grabar el local, se envia automaticamente por firebase
            except:
                logger.info("No se pudo enviar Notificacion")
        except Exception as error:
            logger.info("Fallo finalizar_geotracking: "+str(error)+'\n'+str(traceback.format_exc()))

@background(schedule=30)
def finalizar_geotracking():
    logger.info("Realizamos la finalizacion de los Geotrackings")
    individuos = obtener_trackeados()
    #Obtenemos los que estan siendo trackeados hace mas de 14 dias:
    inicio = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtenemos trackings ya cumplidos:
    geopos_viejas = GeoPosicion.objects.filter(tipo='ST', fecha__lt=inicio)
    #Obtenemos individuos que deben ser liberados
    individuos = individuos.filter(geoposiciones__in=geopos_viejas).distinct()
    #No procesamos los que ya fueron de baja del tracking
    individuos = individuos.exclude(seguimientos__tipo='FT')
    #Los damos de baja:
    for individuo in individuos:
        logger.info("Procesamos: " + str(individuo))
        try:
            st_geopos = individuo.geoposiciones.filter(tipo='ST').last()
            #Generamos seguimiento de Fin de Tracking
            seguimiento = Seguimiento(individuo=individuo)
            seguimiento.tipo = 'FT'
            seguimiento.aclaracion = "Fin de Seguimiento iniciado el: " + str(st_geopos.fecha)[0:16]
            seguimiento.save()
            #Enviamos pushnotification para dar de baja tracking
            #eliminamos si tiene una notificacion esperando
            AppNotificacion.objects.filter(appdata=individuo.appdata).delete()
            #Creamos nueva Notificacion
            try:
                notif = AppNotificacion()
                notif.appdata = individuo.appdata
                notif.titulo = 'Finalizo su periodo bajo Supervicion Digital'
                notif.mensaje = 'Se han cumplido los '+str(DIAS_CUARENTENA)+' dias de seguimiento Obligatorios.'
                notif.accion = 'ST'
                notif.save()#Al grabar el local, se envia automaticamente por firebase
            except:
                logger.info("No se pudo enviar Notificacion")
            #Lo aliminamos de los seguimientos
            individuo.geoperadores.clear()
        except Exception as error:
            logger.info("Fallo finalizar_geotracking: "+str(error)+'\n'+str(traceback.format_exc()))