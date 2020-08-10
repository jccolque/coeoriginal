#Imports Python
import logging
#Imports Django
from django.db.models import Count
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models.signals import post_save, post_delete
#imports Extras
#Imports de la app
from .models import DenunciaAnonima, Consulta
from .models import Telefonista

#Logger
logger = logging.getLogger('signals')

#Definimos señales
@receiver(post_save, sender=DenunciaAnonima)
def asignar_denuncia(created, instance, **kwargs):
    if created:
        telefonistas = Telefonista.objects.all().annotate(cantidad=Count('consultas')+Count('denuncias'))
        for telefonista in telefonistas.filter(tipo__in=("MX", "DE")).order_by('cantidad'):
            if telefonista.max_pendientes > telefonista.cantidad:
                telefonista.denuncias.add(instance)
                break