#Imports Python
import logging
#Imports Django
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports Extras
#Imports del proyecto
from informacion.models import Individuo
#Imports de la app
from .models import Operador

#Logger
logger = logging.getLogger('signals')

#Definimos nuestra señales
@receiver(post_save, sender=Operador)
def asignar_individuo(created, instance, **kwargs):
    if created:
        try:
            instance.individuo = Individuo.objects.get(num_doc=instance.num_doc)
            instance.save()
        except:#Si no existe no hacemos nada
            pass
