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
    for app in CoreConfig.ADMIN_MENU:
        permiso_name = 'operadores.menu_' + app[1]
        print(permiso_name)
        if usuario.has_perm(permiso_name):
            listado.append(app)
    return listado