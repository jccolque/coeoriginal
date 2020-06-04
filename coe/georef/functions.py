#Imports Django
from django.core.cache import cache
#Imports de la app
from .models import Nacionalidad

#Definimos funciones
def obtener_argentina():
    argentina = cache.get("argentina")
    if not argentina:
        argentina = Nacionalidad.objects.filter(nombre__icontains="Argentina").first()
        if not argentina:
            argentina = Nacionalidad(nombre="Argentina")
            argentina.save()
        cache.set("argentina", argentina)
    return argentina