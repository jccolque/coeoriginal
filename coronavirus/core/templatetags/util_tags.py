#Imports de Python
#Imports de Django
from django import template
#Imports de la app

register = template.Library()
#Definimos nuestros tags
@register.simple_tag
def ct_get_from_dict(dict, key):
    try:
        return dict[key]
    except KeyError:
        return None