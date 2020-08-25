#Imports de Python
#Imports de Django
from django import template
from django.utils import timezone

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_color_alerta(config, seguimiento):
    if seguimiento:
        horas = (timezone.now() - seguimiento.fecha).total_seconds() / 3600
        if horas > config.alerta_roja:
            return 'rojo'
        elif horas > config.alerta_amarilla:
            return 'amarillo'
        elif horas > config.alerta_verde:
            return 'verde'
    return 'rojo'