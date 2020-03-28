#Imports de Python
#Imports de Django
from django import template

register = template.Library()
#Definimos nuestros tags
@register.simple_tag
def ct_showlinea(linea):
    str_linea = [linea[0].ref]
    for dato in linea:
        str_linea += [int(dato.valor),]
    print(str_linea)
    return str(str_linea)