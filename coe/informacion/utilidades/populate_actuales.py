#Imports de django
from django.utils import timezone
#imports de la app
from informacion.models import Individuo
from informacion.models import Domicilio, Situacion

def actuales():
    print("Iniciamos la actualizacion de:", Individuo.objects.count(), "Registros")
    individuos_to_update = []
    print("Generando dict de Domicilios. Inicio:", timezone.now())
    domicilios = {d.individuo.id:d for d in Domicilio.objects.all().order_by('fecha').select_related('individuo')}
    print("Generando dict de Situaciones. Inicio:", timezone.now())
    situaciones = {s.individuo.id:s for s in Situacion.objects.all().order_by('fecha').select_related('individuo')}
    print("Empezamos el bucle Gigante:", timezone.now())
    indice = 0
    for i in Individuo.objects.all():
        indice += 1
        if (indice % 15000) == 0:
            print("Se procesaron:", indice, "Registros. Time:", timezone.now())
            Individuo.objects.bulk_update(individuos_to_update, ['domicilio_actual', 'situacion_actual'])
            print("Terminamos el Bulk Update. Time:", timezone.now())
            individuos_to_update = []
        if i.pk in domicilios:
            i.domicilio_actual = domicilios[i.pk]
        if i.pk in situaciones:
            i.situacion_actual = situaciones[i.pk]
        individuos_to_update.append(i)
    #MAndamos bulk update
    print("Se procesaron:", indice, "Registros")
    Individuo.objects.bulk_update(individuos_to_update, ['domicilio_actual', 'situacion_actual'])
    print("Terminamos el Bulk Update. Time:", timezone.now())
    