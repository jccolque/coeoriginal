#Imports de Python
#Imports de Django
from django import template
from django.forms.fields import MultipleChoiceField

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_quitar_del_set(set_relaciones, individuo):
    set_relaciones.remove(individuo)
    return set_relaciones
    