#Imports de Python
#Imports de Django
from django import template

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_color_alerta(alerta):
    print(alerta)
    if alerta == 'DC':
        return 'rojo'
    elif alerta in ('DA', 'FG'):
        return 'naranja'
    elif alerta in ('DA', 'SM'):
        return 'amarillo'
    elif alerta == 'SC':
        return 'verde'