#Imports de Python
#Imports de Django
from django import template
#Imports de la app
from core.apps import CoreConfig

register = template.Library()
#Definimos nuestros tags
@register.simple_tag
def ct_get_grupos(usuario):
    return usuario.groups.all()