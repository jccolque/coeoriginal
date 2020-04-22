#Import django
from django.db.models import Count
#Importamos de la app
from informacion.models import Individuo
from geotracking.models import GeoPosicion, GeOperador

#Definimos funciones
def crear_start_trackings():#Para todos los que estan mandando Registros pero no tienen por falla de sistema.
    individuos = Individuo.objects.filter(geoposiciones__tipo='RG').distinct()
    for individuo in individuos:
        print("Chequeamos a: "+str(individuo))
        if not individuo.geoposiciones.filter(tipo="ST").exists():
            print("Le Creamos ST por que no tenia.\n")
            first_geopos = individuo.geoposiciones.filter(tipo='RG').first()
            geopos = first_geopos
            geopos.pk = None
            geopos.tipo = 'ST'
            geopos.save()

def asignar_geoperadores():
    crear_start_trackings()
    individuos = Individuo.objects.filter(geoposiciones__tipo='ST').distinct()
    for individuo in individuos:
        if not individuo.geoperador.exists():#Si no tiene GeOperador
            print("Le Asignamos Geoperador a: "+str(individuo))
            geoperador = GeOperador.objects.annotate(cantidad=Count('controlados')).order_by('cantidad').first()
            geoperador.controlados.add(individuo)

    