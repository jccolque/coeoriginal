#Imports de Python
#Imports django
#Imports Extras
from background_task import background
#Imports del proyeco
#Import de la app
from .models import Progress_Links

#Rutinas Base:
def crear_progress_link(nombre_tarea):
    p = Progress_Links()
    p.tarea = nombre_tarea
    p.progress_url = '/inscribir/task_progress/' + nombre_tarea
    p.save()
    return nombre_tarea

#Definimos nuestras funciones