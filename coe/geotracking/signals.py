#Imports Python
import logging
#Imports Django
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Count
#imports Extras
#Imports de la app
from .models import GeoPosicion, GeOperador

#Logger
logger = logging.getLogger('signals')

#Definimos nuestra señales
@receiver(post_save, sender=GeoPosicion)
def asignar_geoperador(created, instance, **kwargs):
    if created and instance.tipo == 'ST':#Si lo ingresamos al sistema
        #Obtenemos el que menos controlados tiene
        geoperador = GeOperador.objects.annotate(cantidad=Count('controlados')).order_by('cantidad').first()
        #Se lo agregamos
        geoperador.controlados.add(instance.individuo)