#Imports del proyecto
from informacion.models import Individuo, Atributo
#Imports de la app
from seguimiento.models import Vigia
from seguimiento.functions import obtener_bajo_seguimiento

#Definiciones
def activar_vigilancia():
    #Obtenemos todos los que estan en Cuarentena Obligatoria / Aislamiento
    individuos = Individuo.objects.filter(situacion_actual__conducta__in=('D', 'E'))
    #Evitamos los que ya estan en vigilancia
    individuos = individuos.exclude(atributos__tipo='VE')
    #Optimizamos
    individuos = individuos.select_related('situacion_actual')
    #Generamos el atributo:
    atribs = []
    for individuo in individuos:
        atributo = Atributo(individuo=individuo)
        atributo.tipo = 'VE'
        atributo.fecha = individuo.situacion_actual.fecha
        atributo.aclaracion = "Recuperado Via Sistema (utilidades/recuperar)"
        atribs.append(atributo)
    #Creamos todos:
    Atributo.objects.bulk_create(atribs)

def asignar_vigilancia():
    activar_vigilancia()
    individuos = obtener_bajo_seguimiento()
    #No procesamos a los que ya estan bajo un vigia
    individuos = individuos.filter(vigia=None)
    print("Asignaremos: " + str(individuos.count) + " individuos.")
    #Procesamos
    for individuo in individuos:
        print("Asignamos a " + str(individuo))
        try:
            nuevo_vigia = Vigia.objects.all().annotate(cantidad=Count('controlados')).order_by('cantidad').first()
            nuevo_vigia.controlados.add(controlado)
        except:
            print("No hay vigias")