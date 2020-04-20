#Imports de Python
#Imports de Django
from django import template

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def ct_quitar_del_set(set_relaciones, individuo):
    set_relaciones.remove(individuo.id)
    return set_relaciones

@register.simple_tag
def ct_check_seguir(individuo, set_relaciones):
    for relacion in individuo.relaciones.all():
        if relacion.relacionado.id in set_relaciones:
            return True