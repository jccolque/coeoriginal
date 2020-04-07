#Imports de Python
#Imports django
#Imports Extras
from background_task import background
#Import Personales
from .models import Progress_Links

#Rutinas Base:
def crear_progress_link(nombre_tarea):
    p = Progress_Links()
    p.tarea = nombre_tarea
    p.progress_url = '/inscribir/task_progress/' + nombre_tarea
    p.save()
    return nombre_tarea

#Tarea de creacion masiva de items
@background(schedule=60)
def bulkcreate_2_db(model, segmento):
    model.objects.bulk_create(segmento)

def crear_elementos(model, items, nombre_tarea):
    segmento = []
    for item in items:
        segmento.append(item)
        if len(segmento) == 1000:#si acumulamos 50 individuos
            nueva_tarea = crear_progress_link(nombre_tarea+'-'+str(len(items)/50))
            bulkcreate_2_db(model, segmento, queue=nueva_tarea)
            segmento = []#Vaciamos el segmento ya enviado a tarea
    #Los rezagados
    nueva_tarea =  crear_progress_link(nombre_tarea+':'+str(len(items)/50))
    bulkcreate_2_db(model, segmento, queue=nueva_tarea)
