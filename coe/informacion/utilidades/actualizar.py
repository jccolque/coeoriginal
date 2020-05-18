#Imports del proyecto
from informacion.models import Individuo
from seguimiento.models import Seguimiento

def agregar_seguimiento():
    #Obtenemos todos los individuos que hayan estado aislados
    individuos = Individuo.objects.filter(domicilios__aislamiento=True)
    #Pero excluimos los que ya estan en seguimiento
    individuos = individuos.exclude(seguimientos__tipo='I')
    #Optimizamos
    individuos = individuos.prefetch_related('domicilios')
    #Generamos los seguimientos que nos faltan
    segs = []
    for individuo in individuos:
        seguimiento = Seguimiento(individuo=individuo)
        seguimiento.tipo = 'I'
        seguimiento.fecha = individuo.domicilios.filter(aislamiento=True).last().fecha
        seguimiento.aclaracion = "Autogenerado por ingreso a aislamiento"
        segs.append(seguimiento)
    #Terminamos de generarlos:
    Seguimiento.objects.bulk_create(segs)