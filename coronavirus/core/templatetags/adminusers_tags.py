#Imports de Python
import ast
#Imports de Django
from django import template

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def crear_link_addadmin(app_name):
    return '/'+app_name.lower()+'/crear_admin'

@register.simple_tag
def ct_changes_to_list(changes):
    cambios = []
    for campo,values in ast.literal_eval(changes).items(): 
        cambios.append(campo+': '+values[0]+'>'+values[1])
    return cambios

@register.simple_tag
def ct_model_name(objeto):
    return objeto.content_type.name
