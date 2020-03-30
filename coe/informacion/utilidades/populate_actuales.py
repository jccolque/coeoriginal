
from background_task import background
#Imports del proyecto
from background.tasks import crear_progress_link
#Imports de la app
from informacion.models import Individuo
from informacion.models import Domicilio, Situacion

@background(schedule=1)
def masive_update(individuos_to_update):
    print("Lanzamos el Bulk Update")
    Individuo.objects.bulk_update(individuos_to_update, ['domicilio_actual', 'situacion_actual'])

def actuales():
    tarea = crear_progress_link('CARGAR ACTUALES')
    individuos_to_update = []
    print("Iniciamos la actualizacion de:", Individuo.objects.count(), "Registros")
    domicilios = {d.individuo.id:d for d in Domicilio.objects.all().order_by('fecha').select_related('individuo')}
    print("Generamos dict de Domicilios")
    situaciones = {s.individuo.id:s for s in Situacion.objects.all().order_by('fecha').select_related('individuo')}
    print("Genramos dict de Situaciones")
    indice = 0
    for i in Individuo.objects.all():
        indice += 1
        if (indice % 10000) == 0:
            print("Se procesaron:", indice, "Registros")
            #MAndamos bulk update
            masive_update(individuos_to_update, queue=tarea)
            #Blanqueamos para el proximo batch
            individuos_to_update = []
        if i.pk in domicilios:
            i.domicilio_actual = domicilios[i.pk]
        if i.pk in situaciones:
            i.situacion_actual = situaciones[i.pk]
        individuos_to_update.append(i)