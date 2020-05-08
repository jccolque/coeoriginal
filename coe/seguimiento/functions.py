#Imports del Proyeto
from informacion.models import Individuo
#Imports de la app
from .models import Vigia

#Definimos funciones
def obtener_bajo_seguimiento():
    individuos = Individuo.objects.filter(atributos__tipo='VE')
    individuos = individuos.exclude(seguimientos__tipo='FS')
    return individuos