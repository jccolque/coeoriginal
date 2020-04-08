#Imports de la app
from django.contrib.auth.models import Permission
from .models import Operador

#Definimos funciones del modulo
def obtener_operador(request):
    try:
        return Operador.objects.get(usuario=request.user)
    except Operador.DoesNotExist:
        return None

def obtener_permisos(usuario=None):
    if usuario and not usuario.is_superuser:
        return Permission.objects.filter(user=usuario)
    else:
        return Permission.objects.filter(
            content_type__app_label='operadores',
            content_type__model='operador').exclude(name__contains='Can ').order_by('id')