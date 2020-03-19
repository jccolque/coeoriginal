#Imports Python

#Imports Django
from django.core.cache import cache
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports del proyecto
from georef.functions import get_paises_riesgo
#Imports de la app
from .models import Individuo, Situacion
from .models import Atributo, TipoAtributo

#Definimos nuestra señales
@receiver(post_save, sender=Individuo)
def crear_situacion(created, instance, **kwargs):
    if created:
        #   Vejez +60 años
        if instance.fecha_nacimiento < (timezone.now().date() - relativedelta(years=60)):
            try:
                atributo = Atributo()
                atributo.individuo = instance
                atributo.tipo = TipoAtributo.objects.filter(nombre__icontains='poblacion').first()
            except TipoAtributo.DoesNotExist:
                print('No existe Atributo de Poblacion de Riesgo')
        #Situacion:
        situacion = Situacion()
        situacion.individuo = instance
        situacion.save()
        