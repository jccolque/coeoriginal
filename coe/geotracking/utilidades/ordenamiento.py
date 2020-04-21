#Importamos de la app
from geotracking.models import GeoPosicion, GeOperador

#Definimos funciones
def asignar_geoperadores():
    geos = GeoPosicion.objects.filter(tipo='ST')
    