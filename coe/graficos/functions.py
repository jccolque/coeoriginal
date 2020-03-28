from .models import Grafico

def obtener_grafico(nombre, verbose_name, tipo):
    try:
        return Grafico.objects.get(nombre=nombre, verbose_name=verbose_name, tipo=tipo)
    except Grafico.DoesNotExist:
        grafico = Grafico()
        grafico.nombre = nombre
        grafico.verbose_name = verbose_name
        grafico.tipo = tipo
        grafico.save()
        return grafico