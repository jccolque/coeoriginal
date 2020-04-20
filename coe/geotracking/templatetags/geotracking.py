#Imports de Python
#Imports de Django
from django import template

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_color_alerta(alerta):
    if alerta == 'DC':
        return 'rojo'
    elif alerta in ('DA', 'FG'):
        return 'naranja'
    elif alerta in ('DA', 'SM'):
        return 'amarillo'
    elif alerta == 'SC':
        return 'verde'

@register.simple_tag
def ct_icon_map(geopos):
    icono = 'normal'
    #Por tipo
    if geopos.tipo == 'ST':#Si inicio el tracking
        icono = 'hogar_rojo'
    elif geopos.tipo == 'PC':#Si es el origen de control
        icono = 'hogar'
    elif geopos.tipo == 'RG':#Si es un tracking
        icono = 'pasitos'
    elif geopos.tipo == 'CG':
        icono = 'policia'
    #Por alerta
    if geopos.alerta != 'SA':
        icono = 'alerta'
        if geopos.procesada:
            if geopos.tipo == 'CG':
                icono = 'policia_rojo'
            else:
                icono = 'alerta_procesada'
    #Si no entro por ninguno de estos
    return icono