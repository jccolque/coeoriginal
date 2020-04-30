from georef.models import Ubicacion

def reparar_ocupacion():
    ubicaciones = Ubicacion.objects.filter(tipo='AI')
    for ubicacion in ubicaciones:
        print('\n')
        print(ubicacion.nombre + ' | Capacidad Actual: ' + str(ubicacion.capacidad_ocupada))
        ubicacion.capacidad_ocupada = ubicacion.aislados_actuales().count()
        print('Actualizado a: ' + str(ubicacion.capacidad_ocupada))
        ubicacion.save()