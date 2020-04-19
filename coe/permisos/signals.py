#Imports Python
import logging
#Imports Django
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports Extras
#Imports de la app
from .models import IngresoProvincia

#Logger
logger = logging.getLogger('signals')

#Definimos nuestra señales
@receiver(post_save, sender=IngresoProvincia)
def enviar_mail_aprobacion(instance, **kwargs):
    if instance.estado == 'A':
        pass#Mandar mail de que fue aprobado