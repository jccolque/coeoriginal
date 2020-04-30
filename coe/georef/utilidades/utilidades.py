from informacion.models import Individuo

def reparar_ocupacion():
    ubicaciones = Ubicacion.objects.filter(tipo='AI')
    for ubicacion in ubicaciones:
        ubicacion.capacidad_ocupada = ubicacion.aislados_actuales.count()