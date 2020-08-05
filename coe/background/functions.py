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
        ts = Task.objects.filter(run_at__lt=timezone.now() - timedelta(minutes=1))
        ts = ts.exclude(repeat=0)
        ts.delete()
    except:
        logger = logging.getLogger("tasks")
        logger.info("Falla: "+str(traceback.format_exc()))

def inicializar_background_job(function, intervalo, function_name):
    #Tareas Background:
    try:
        from background_task.models import Task#Traemos el modelo de tareas programadas
        if not Task.objects.filter(verbose_name=function_name).exists():#Solo si no existe
            if isinstance(intervalo, int):#si es una cantidad
                function(repeat=intervalo * 3600, verbose_name=function_name)
            else:#Si es una constante
                function(repeat=intervalo, verbose_name=function_name)
    except:
        logger = logging.getLogger("tasks")
        logger.info("Falla: "+str(traceback.format_exc()))

def hasta_madrugada(minutos_extra):
    #obtenemos horas faltantes para las 12
    falta_medianoche = 24 - timezone.now().time().hour
    #Agregamos 2 horas
    hasta_las_2 = falta_medianoche + 2
    #Transformamos en minutos
    hasta_las_2 = hasta_las_2 * 60
    #Agregamos los minutos extras:
    hasta_las_2 += minutos_extra
    #Devolvemos en segundos
    return hasta_las_2 * 60
