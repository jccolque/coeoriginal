
from django.urls import reverse
#Imports de Django
from django import template

register = template.Library()
@register.inclusion_tag('extras/qr_tag.html', takes_context=True)
def get_qrcode_image(context, text, size):
    url = reverse('generate_qr')
    return {'url': url, 'text': text, 'size': size}