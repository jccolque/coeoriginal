#Imports de Python
#Imports de Django
from django import template
from django.utils import timezone

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_horas_desde(fecha):
    return (timezone.now() - fecha).total_seconds() / 3600

@register.simple_tag
def ct_color_alerta(seguimiento):
    horas = (timezone.now() - fecha).total_seconds() / 3600
    if horas > 48:
        return 'rojo'
    elif horas > 24:
        return 'naranja'
    elif horas > 12:
        return 'amarillo'
    else:
        return 'verde'
