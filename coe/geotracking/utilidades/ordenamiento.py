#Import django
from django.db.models import Count
#Importamos de la app
from informacion.models import Individuo
from geotracking.models import GeoPosicion, GeOperador

#Definimos funciones
def crear_start_trackings():#Para todos los que estan mandando Registros pero no tienen por falla de sistema.
    individuos = Individuo.objects.filter(geoposiciones__tipo='RG')
    individuos = individuos.exclude(geoposiciones__tipo="ST")
    for individuo in individuos:
        first_geopos = individuo.geoposiciones.filter(tipo='RG').first()
        geopos = first_geopos
        geopos.pk = None
        geopos.tipo = 'ST'
        geopos.save()

def asignar_geoperadores():
    crear_start_trackings()
    individuos = Individuo.objects.filter(geoposiciones__tipo='ST')
    for individuo in individuos:
        if not individuo.geoperador.exists():#Si no tiene GeOperador
            geoperador = GeOperador.objects.annotate(cantidad=Count('controlados')).order_by('cantidad').first()
            geoperador.add_trackeado(individuo)

    