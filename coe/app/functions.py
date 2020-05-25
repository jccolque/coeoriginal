#Imports de python
import traceback
import logging
#Imports de la app
from .models import AppNotificacion

#Definimos logger
logger = logging.getLogger("functions")

#Funciones basicas:
def obtener_dni(data):
    if "dni" in data:
        return str(data["dni"]).upper()
    else:
        return str(data["dni_individuo"]).upper()

#Funcionalidades
def activar_tracking(individuo):
    try:
        AppNotificacion.objects.filter(appdata=individuo.appdata).delete()
        notif = AppNotificacion(appdata=individuo.appdata)
        notif.titulo = 'Iniciar Proceso de Supervisión Digital'
        notif.mensaje = 'Por Favor presione esta notificacion para Iniciarlo.'
        notif.accion = 'BT'
        notif.save()#Al grabar el local, se envia automaticamente por firebase (signals)
    except Exception as e:
        logger.info("\nFallo Activar Tracking: "+str(individuo))
        logger.info(e)
        logger.info(traceback.format_exc())

def desactivar_tracking(individuo):
    try:
        AppNotificacion.objects.filter(appdata=individuo.appdata).delete()
        notif = AppNotificacion(appdata=individuo.appdata)
        notif.titulo = 'Finalizar Proceso de Supervisión Digital'
        notif.mensaje = 'Por Favor presione esta notificacion para Finalizarlo.'
        notif.accion = 'ST'
        notif.save()#Al grabar el local, se envia automaticamente por firebase (signals)
    except Exception as e:
        logger.info("\nFallo Desactivar Tracking: "+str(individuo))
        logger.info(e)
        logger.info(traceback.format_exc())
    