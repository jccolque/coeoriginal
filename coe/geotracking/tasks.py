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
from background.functions import hasta_madrugada
from seguimiento.models import Seguimiento
from app.models import AppNotificacion
#Import de la app
from .models import GeoPosicion
from .functions import obtener_trackeados

#Definimos logger
logger = logging.getLogger("tasks")

#Definimos tareas
@background(schedule=hasta_madrugada(30))
def geotrack_sin_actualizacion():
    logger.info("\nGeoTrackings Sin actualizar")
    individuos = obtener_trackeados()
    #Quitamos los que enviaron Posicion GPS en las ultimas 4 horas:
    limite = timezone.now() - timedelta(hours=4)
    posiciones_actuales = GeoPosicion.objects.filter(fecha__gt=limite, tipo='RG')
    individuos = individuos.exclude(geoposiciones__in=posiciones_actuales)
    #Quitamos los que ya generamos alerta y aun no se proceso
    alertas_activas = GeoPosicion.objects.filter(alerta='FG', procesada=False)
    individuos = individuos.exclude(geoposiciones__in=alertas_activas)
    #Recorrer y alertar
    for individuo in individuos:
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

@background(schedule=hasta_madrugada(20))
def vencer_alertas():
    #Obtenemos todas las geopos que son alerta
    alertas = GeoPosicion.objects.exclude(alerta='SA')
    #Eliminamos las procesadas
    alertas = alertas.exclude(procesada=True)
    alertas = alertas.exclude(alerta='FP')#Tampoco las de sin permiso
    #Obtenemos todas las viejas
    limite = timezone.now() - timedelta(hours=24 * 7)#Una semana
    alertas = alertas.filter(fecha__lt=limite)
    #Las cancelamos
    alertas.update(procesada=True, aclaracion="Dada de baja por vencimiento")

@background(schedule=hasta_madrugada(15))
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
            for geoperador in individuo.geoperadores.all():
                geoperador.del_trackeado(individuo)
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
