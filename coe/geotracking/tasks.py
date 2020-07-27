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
from seguimiento.models import Seguimiento
from app.models import AppNotificacion
#Import de la app
from .models import GeoPosicion
from .functions import obtener_trackeados

#Definimos logger
logger = logging.getLogger("tasks")

#Definimos tareas
@background(schedule=30)
def geotrack_sin_actualizacion():
    logger.info("\nGeoTrackings Sin actualizar")
    individuos = obtener_trackeados()
    #Quitamos los que enviaron Posicion GPS en las ultimas 2 horas:
    limite = timezone.now() - timedelta(hours=4)
    individuos = individuos.exclude(geoposiciones__in=GeoPosicion.objects.filter(fecha__gt=limite, tipo='RG'))
    #Quitamos los que ya generamos alerta y aun no se proceso
    individuos = individuos.exclude(geoposiciones__in=GeoPosicion.objects.filter(alerta='FG', procesada=False))
    #Recorrer y alertar
    for individuo in individuos:
        logger.info("Procesamos: " + str(individuo))
        try:
            geopos = individuo.geoposiciones.last()
            geopos.alerta = 'FG'
            geopos.procesada = False
            horas = int((geopos.fecha - timezone.now()).total_seconds() / 3600)
            geopos.aclaracion = "Lleva " + str(horas) + "hrs sin informar posicion."
            geopos.save()
            #eliminamos si tiene una notificacion esperando
            AppNotificacion.objects.filter(appdata=individuo.appdata).delete()
            #Creamos nueva Notificacion
            if individuo.appdata:
                try:
                    notif = AppNotificacion()
                    notif.appdata = individuo.appdata
                    notif.titulo = 'Falta de Seguimiento'
                    notif.mensaje = geopos.aclaracion
                    notif.accion = 'SL'
                    notif.save()#Al grabar el local, se envia automaticamente por firebase
                    logger.info("Notificado Via App")
                except:
                    logger.info("No se pudo enviar Notificacion")
        except Exception as error:
            logger.info("Fallo: "+str(error)+':\n'+str(traceback.format_exc()))

@background(schedule=25)
def vencer_alertas():
    #Obtenemos todasl as alertas vencidas
    alertas = GeoPosicion.objects.filter(procesada=False)
    #Eliminamos las que no son alerta
    alertas = alertas.exclude(alerta='SA')
    alertas = alertas.exclude(alerta='FP')#Tampoco las de sin permiso
    #Filtramos
    limite = timezone.now() - timedelta(hours=24 * 7)#Una semana
    alertas = alertas.filter(fecha__lt=limite)
    alertas.update(procesada=True, aclaracion="Dada de baja por vencimiento")

@background(schedule=15)
def finalizar_geotracking():
    logger.info("\nRealizamos la finalizacion de los Geotrackings")
    individuos = obtener_trackeados()
    #Obtenemos los que estan siendo trackeados hace mas de 14 dias:
    inicio = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtenemos trackings ya cumplidos:
    geopos_viejas = GeoPosicion.objects.filter(tipo='ST', fecha__lt=inicio)
    #Obtenemos individuos que deben ser liberados
    individuos = individuos.filter(geoposiciones__in=geopos_viejas)
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
            #Lo quitamos de los paneles de control:
            individuo.geoperadores.clear()
            #Enviamos pushnotification para dar de baja tracking
            #eliminamos si tiene una notificacion esperando
            AppNotificacion.objects.filter(appdata=individuo.appdata).delete()
            #Creamos nueva Notificacion
            if individuo.appdata:
                try:
                    notif = AppNotificacion()
                    notif.appdata = individuo.appdata
                    notif.titulo = 'Finalizo su periodo bajo Supervicion Digital'
                    notif.mensaje = 'Se han cumplido los '+str(DIAS_CUARENTENA)+' dias de seguimiento Obligatorios.'
                    notif.accion = 'ST'
                    notif.save()#Al grabar el local, se envia automaticamente por firebase
                    logger.info("Notificado Via App")
                except:
                    logger.info("No se pudo enviar Notificacion")
        except Exception as error:
            logger.info("Fallo finalizar_geotracking: "+str(error)+':\n'+str(traceback.format_exc()))