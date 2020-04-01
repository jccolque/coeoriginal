
#Definimos nuestras funciones reutilizables
def obtener_relacionados(individuo, relaciones):
    if individuo not in relaciones:
        relaciones.add(individuo)
        for relacion in individuo.relaciones.all():
            obtener_relacionados(relacion.relacionado, relaciones)
    return relaciones