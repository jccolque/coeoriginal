#Imports de python
import logging
import traceback
#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from coe.settings import DEBUG, LOADDATA
from core.functions import agregar_menu

class GeotrackingConfig(AppConfig):
    name = 'geotracking'
    def ready(self):
        agregar_menu(self)
        #Señales
        if not LOADDATA:
            from .signals import asignar_geoperador
            from .signals import inicio_seguimiento
        #Tareas Background:
        try:
            if not DEBUG:
                from background_task.models import Task
                if not Task.objects.filter(verbose_name="geotrack_sin_actualizacion").exists():
                    from geotracking.tasks import geotrack_sin_actualizacion
                    geotrack_sin_actualizacion(repeat=3600 * 6, verbose_name="geotrack_sin_actualizacion")#Cada una hora
                #if not Task.objects.filter(verbose_name="finalizar_geotracking").exists():
                #    from geotracking.tasks import finalizar_geotracking
                #    finalizar_geotracking(repeat=3600*12, verbose_name="finalizar_geotracking")#Cada 12 horas
        except OperationalError:
            logger = logging.getLogger("tasks")
            logger.info("Falla: "+str(traceback.format_exc()))