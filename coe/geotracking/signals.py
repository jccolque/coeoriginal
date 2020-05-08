#Imports Python
import logging
#Imports Django
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Count
#imports Extras
#Imports del proyecto
from seguimiento.models import Seguimiento
#Imports de la app
from .models import GeoPosicion, GeOperador

#Logger
logger = logging.getLogger('signals')

#Definimos nuestra señales
@receiver(post_save, sender=GeoPosicion)
def asignar_geoperador(created, instance, **kwargs):
    if created and instance.tipo == 'ST':#Si lo ingresamos al sistema
        try:
            #Obtenemos el que menos controlados tiene
            geoperador = GeOperador.objects.annotate(cantidad=Count('controlados')).order_by('cantidad').first()
            #Se lo agregamos
            geoperador.controlados.add(instance.individuo)
        except:
            logger.info("Falla: Aun no existen geoperadores disponibles!")

@receiver(post_save, sender=GeoPosicion)
def inicio_seguimiento(created, instance, **kwargs):
    if created and instance.tipo == 'ST':#Si lo ingresamos al sistema
        seguimiento = Seguimiento(individuo=instance.individuo)
        seguimiento.tipo = 'IT'
        seguimiento.aclaracion = "Autogenerado"
        seguimiento.save()