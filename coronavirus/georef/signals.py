#Imports Python
#Imports de Django
from django.dispatch import receiver
from django.db.models.signals import post_save
#Imports del proyeceto
from empresas.models import Paraje
#Imports de la app
from .models import Localidad

#Definimos nuestras señales
@receiver(post_save, sender=Localidad)
def crear_paraje(instance, created, **kwargs):
    if created:
        paraje = Paraje()
        paraje.departamento = instance.departamento
        paraje.nombre = instance.nombre
        paraje.save()