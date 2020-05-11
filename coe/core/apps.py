#Imports de python
import logging
import traceback
#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from coe.settings import LOADDATA

class CoreConfig(AppConfig):
    name = 'core'
    ADMIN_MENU = []
    ADMIN_MODELS = {}
    def ready(self):
        #Señales
        if not LOADDATA:
            from .signals import enviar_mail_new_user
        #Eliminamos todas las tareas previas para iniciar las nuevas
        try:
            from background_task.models import Task, CompletedTask
            Task.objects.all().delete()
            CompletedTask.objects.all().delete()
        except:
            logger = logging.getLogger("tasks")
            logger.info("Falla: "+str(traceback.format_exc()))