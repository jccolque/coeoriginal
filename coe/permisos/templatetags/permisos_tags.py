#Imports de Python
#Imports de Django
from django import template
#Imports del proyecto
from permisos.choices import TIPO_PERMISO
#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_nombre_permiso(choice_id):
    for tipo in TIPO_PERMISO:
        if choice_id == tipo[0]:
            return tipo[1]

@register.simple_tag
def ct_tiene_permiso(nivel, choice_id):
    if choice_id in nivel.tramites_admitidos:
        return '/static/img/icons/check.png'
    else:
        return '/static/img/icons/wrong.png'