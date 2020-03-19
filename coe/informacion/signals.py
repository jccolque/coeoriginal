#Imports Python

#Imports de Django
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports del proyecto

#Imports de la app
from .models import Individuo, Situacion

#Definimos nuestra señales
@receiver(post_save, sender=Individuo)
def crear_situacion(created, instance, **kwargs):
    if created:
        situacion = Situacion()
        situacion.individuo = instance
        situacion.save()
        pass