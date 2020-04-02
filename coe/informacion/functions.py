
#Definimos nuestras funciones reutilizables
def obtener_relacionados(individuo, relaciones):
    if individuo.id not in relaciones:
        relaciones.add(individuo.id)
        for relacion in individuo.relaciones.select_related('individuo', 'relacionado').all():
            obtener_relacionados(relacion.relacionado, relaciones)
    return relaciones