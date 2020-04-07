from .models import Grafico

def obtener_grafico(nombre, verbose_name, tipo):
    try:
        graficos = Grafico.objects.prefetch_related('columnas', 'columnas__datos')
        grafico = graficos.get(nombre=nombre, verbose_name=verbose_name, tipo=tipo)
        return grafico
    except Grafico.DoesNotExist:
        grafico = Grafico()
        grafico.nombre = nombre
        grafico.verbose_name = verbose_name
        grafico.tipo = tipo
        grafico.save()
        return grafico