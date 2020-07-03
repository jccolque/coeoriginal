#Imports de Python
#Imports de Django
from django import template
#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_show_file(filefield):
    try:
        if filefield:
            ext = filefield.url.split('.')[-1]
            if ext == 'pdf':
                return "Descargar Archivo"
            else:
                return "<img class='fotos' src='"+filefield.url+"'>"
    except:
        return "Archivo Inaccesible"