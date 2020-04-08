#Imports Django
from django.core.cache import cache
#Imports de la app
from .models import Nacionalidad

#Definimos funciones
def get_paises_riesgo():
    paises_riesgo = cache.get("paises_riesgo")
    if not paises_riesgo:
        paises_riesgo = Nacionalidad.objects.filter(riesgo=True)
        cache.set("paises_riesgo", paises_riesgo)
    return paises_riesgo