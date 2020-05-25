#Imports Python
import logging
import traceback
#Imports de Django
from django.dispatch import receiver
from django.db.models.signals import post_save
#Imports extras
from fcm_django.models import FCMDevice
#Imports del proyeceto
#Imports de la app
from .models import AppNotificacion

#Logger
logger = logging.getLogger('signals')

#Definimos nuestras señales
@receiver(post_save, sender=AppNotificacion)
def enviar_push(instance, created, **kwargs):
    if created:#Si creamos la local, mandamos la push.
        try:
            device = FCMDevice.objects.get(name=instance.appdata.individuo.num_doc)
            device.send_message(
                title=instance.titulo,
                body=instance.mensaje,
            )#La accion la lee al consultar el mensaje grabado.
        except Exception as e:
            logger.info("No se envio mensaje a: " + str(instance.appdata.individuo))
            logger.info(e)
            logger.info(traceback.format_exc())