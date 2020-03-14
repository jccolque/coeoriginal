#Imports de Python
#Imports de Django
from django import template
from django.forms.fields import MultipleChoiceField

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def abrir_alineado(form, field):
    if hasattr(form, 'alinear'):#se instancia en el init del form
        for linea in form.alinear:
            if field.name == linea[0]:
                return True
    return False

@register.simple_tag
def cerrar_alineado(form, field):
    if hasattr(form, 'alinear'):#se instancia en el init del form
        for linea in form.alinear:
            if field.name == linea[-1]:
                return True
    return False

@register.simple_tag
def calcular_ancho(form, field):
    if hasattr(form, 'alinear'):#se instancia en el init del form
        for linea in form.alinear:
            if field.name in linea:
                return int(12 / len(linea))
    return 12

@register.simple_tag
def alineado(form, field):
    if hasattr(form, 'alinear'):#se instancia en el init del form
        for linea in form.alinear:
            if field.name in linea:
                return True
    return False