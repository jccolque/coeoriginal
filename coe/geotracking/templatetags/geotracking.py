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
    if geopos.tipo == 'AD':#Si es autodiagnostico
        icono = 'autodiagnostico'
    elif geopos.tipo == 'TS':
        icono = 'test'
    elif geopos.tipo == 'ST':#Si inicio el tracking
        icono = 'hogar_rojo'
    elif geopos.tipo == 'PC':#Si es el origen de control
        icono = 'hogar'
    elif geopos.tipo == 'RG':#Si es un tracking
        icono = 'pasitos'
    elif geopos.tipo == 'CG':
        icono = 'policia'
    #Por alerta
    if geopos.alerta != 'SA':
        if geopos.tipo == 'RG':
            icono = 'alerta'
        elif geopos.procesada:
            if geopos.tipo == 'CG':
                icono = 'policia_rojo'
            else:
                icono = 'alerta_procesada'
    #Si no entro por ninguno de estos
    return icono

@register.simple_tag
def ct_icon_map2(geopos):
    icono = "/img/icons/maps/house_red.png"
    #Por tipo
    if geopos.tipo == 'AD':#Si es autodiagnostico
        icono = "/img/icons/maps/autodiagnostico.png"
    elif geopos.tipo == 'TS':
        icono = "/img/icons/maps/test.png"
    elif geopos.tipo == 'ST':#Si inicio el tracking
        icono = "/img/icons/maps/house_red.png"
    elif geopos.tipo == 'PC':#Si es el origen de control
        icono = "/img/icons/maps/house.png"
    elif geopos.tipo == 'RG':#Si es un tracking
        icono = "/img/icons/maps/steps.png"
    elif geopos.tipo == 'CG':
        icono = "/img/icons/maps/detective.png"
    #Por alerta
    if geopos.alerta != 'SA':
        if geopos.tipo == 'RG':
            icono = "/img/icons/maps/alerta.png"
        elif geopos.procesada:
            if geopos.tipo == 'CG':
                icono = "/img/icons/maps/detective_red.png"
            else:
                icono = "/img/icons/maps/alerta_procesada.png"
    #Si no entro por ninguno de estos
    return icono