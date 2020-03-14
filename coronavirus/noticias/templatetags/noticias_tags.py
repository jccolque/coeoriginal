#Imports Django
from django import template
#Imports del proyecto
from noticias.models import Noticia

#Declaramos
register = template.Library()

#Definimos nuestros tags
@register.simple_tag
def get_destacadas():
    return Noticia.objects.filter(destacada=True)[:5]


@register.simple_tag
def get_etiquetas():
    return Noticia.etiquetas.most_common()[:10]