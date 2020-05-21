#Imports Python
import logging
#Imports Django
from django.utils import timezone
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
#imports Extras
#Imports de la app
from .models import NivelRestriccion, PasajeroCirculacion

#Logger
logger = logging.getLogger('signals')

#Definimos nuestra señales
@receiver(post_save, sender=NivelRestriccion)
def activar_restriccion(created, instance, **kwargs):
    if instance.activa:
        #Chequeamos todos los permisos para que cumplan los cambios
        # BLA BLA BLA
        if not instance.fecha_activacion:#Si la acabamos de activar:
            #Desactivamos las otras
            NivelRestriccion.objects.exclude(pk=instance.pk).update(activa=False)
            instance.fecha_activacion = timezone.now()
            instance.save()
            cache.set("nivel_restriccion", instance)#La dejamos cacheada

@receiver(pre_save, sender=PasajeroCirculacion)
def cargar_individuo(created, instance, **kwargs):
    instance.individuo = instance.get_individuo()