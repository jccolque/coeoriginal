from .models import Grafico

def obtener_grafico(nombre, tipo):
    try:
        return Grafico.objects.get(nombre=nombre, tipo=tipo)
    except Grafico.DoesNotExist:
        grafico = Grafico()
        grafico.nombre = nombre
        grafico.tipo = tipo
        grafico.save()
        return grafico