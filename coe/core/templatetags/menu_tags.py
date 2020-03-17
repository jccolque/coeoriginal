#Imports de Python
#Imports de Django
from django import template
#Imports de la app
from core.apps import CoreConfig

register = template.Library()
#Definimos nuestros tags
@register.simple_tag
def ct_opciones(usuario):
    listado = []
    if usuario.has_perm('operadores.menu_operadores'):
        listado = [app for app in CoreConfig.ADMIN_MENU]
    return listado