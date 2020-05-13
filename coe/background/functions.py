#Imports de Python
import logging
import traceback
from datetime import timedelta
#Imports django
from django.utils import timezone
#Imports Extras
from background_task import background
#Imports del proyeco
from coe.settings import DEBUG
#Import de la app
from .models import Progress_Links

#Rutinas Base:
def crear_progress_link(nombre_tarea):
    p = Progress_Links()
    p.tarea = nombre_tarea
    p.progress_url = '/inscribir/task_progress/' + nombre_tarea
    p.save()
    return nombre_tarea

def limpiar_background_viejas():
    try:
        from background_task.models import Task
        ts = Task.objects.filter(run_at__lt=timezone.now() - timedelta(minutes=5))
        ts = ts.exclude(repeat=0)
        ts.delete()
    except:
        logger = logging.getLogger("tasks")
        logger.info("Falla: "+str(traceback.format_exc()))

def inicializar_background_job(function, horas, function_name):
    #Tareas Background:
    try:
        from background_task.models import Task
        if not Task.objects.filter(verbose_name=function_name).exists():
            function(repeat=3600 * horas, verbose_name=function_name)
    except:
        logger = logging.getLogger("tasks")
        logger.info("Falla: "+str(traceback.format_exc()))