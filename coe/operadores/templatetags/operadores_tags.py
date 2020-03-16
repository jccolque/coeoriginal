#Imports Django
from django import template
#Imports del proyecto

#Declaramos
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_get_fecha(operador, dict_eventos):
    try:
        return dict_eventos[operador.id].fecha.strftime("%d/%m/%Y, %H:%M:%S")
    except KeyError:
        return 'Sin registro'