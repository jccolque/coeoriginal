#Imports de la app
from .models import Operador

#Definimos funciones del modulo
def obtener_operador(request):
    try:
        return Operador.objects.get(usuario=request.user)
    except Operador.DoesNotExist:
        return None
