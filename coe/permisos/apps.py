#Imports de python
import logging
import traceback
#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from coe.settings import DEBUG, LOADDATA
from core.functions import agregar_menu

class PermisosConfig(AppConfig):
    name = 'permisos'
    def ready(self):
        agregar_menu(self)
        #Cargamos signals
        if not LOADDATA:
            from .signals import activar_restriccion
            from .signals import cargar_individuo
        # Background Jobs
        try:
            if not DEBUG:
                from background_task.models import Task
                if not Task.objects.filter(verbose_name="eliminar_ingresos_provinciales").exists():
                    from permisos.tasks import eliminar_ingresos_provinciales
                    eliminar_ingresos_provinciales(repeat=3600 * 24, verbose_name="eliminar_ingresos_provinciales")#cada 24 horas
        except:
            logger = logging.getLogger("tasks")
            logger.info("Falla: "+str(traceback.format_exc()))
