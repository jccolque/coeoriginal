from georef.models import Ubicacion

def reparar_ocupacion():
    ubicaciones = Ubicacion.objects.filter(tipo='AI')
    for ubicacion in ubicaciones:
        print('\n')
        print(ubicacion.nombre + '(' + str(ubicacion.pk) + ')'+ '| Capacidad Actual: ' + str(ubicacion.capacidad_ocupada))
        ubicacion.capacidad_ocupada = len(ubicacion.aislados_actuales())
        print('Actualizado a: ' + str(ubicacion.capacidad_ocupada))
        ubicacion.save()