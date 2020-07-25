#Imports del proyecto
from operadores.functions import obtener_operador
#Imports de la app
from .models import Telefonista

#Definimos funciones de la app
def obtener_telefonista(request):
    operador = obtener_operador(request)
    if operador:
        return Telefonista.objects.filter(operador=operador).first()