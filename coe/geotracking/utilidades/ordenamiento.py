#Importamos de la app
from informacion.models import Individuo
from geotracking.models import GeoPosicion, GeOperador

#Definimos funciones
def crear_start_trackings():
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