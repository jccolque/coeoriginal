#Imports Django
from django import template
#Imports del proyecto
#Imports de la app
from operadores.functions import obtener_operador
#Declaramos
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_get_fecha(operador, dict_eventos):
    try:
        return dict_eventos[operador.id].fecha.strftime("%d/%m/%Y, %H:%M:%S")
    except KeyError:
        return 'Sin registro'

@register.simple_tag
def ct_get_operador(request):
    return obtener_operador(request)