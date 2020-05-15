#Imports de Python
#Imports de Django
from django import template
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

#Iniciamos el registro de tags en el procesador de templates
register = template.Library()

@register.simple_tag
def ct_auditar_obj_url(obj):
    ct_id = ContentType.objects.get_for_model(obj).id
    #Generamos url:
    return reverse('operadores:auditar_cambios', kwargs={'content_id': ct_id, 'object_id': obj.id})