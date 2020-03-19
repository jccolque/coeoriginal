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
        #Atributos:
        #   Pais de Riesgo
        paises = get_paises_riesgo()
        if (instance.nacionalidad in paises) or (instance.origen in paises):
            try:
                atributo = Atributo()
                atributo.individuo = instance
                atributo.tipo = TipoAtributo.objects.get(nombre__icontains='Pais de Riesgo')
            except TipoAtributo.DoesNotExist:
                print('No existe Atributo de Pais de Riesgo')
        #   Vejez +60 años
        if instance.fecha_nacimiento < (timezone.now().date() - relativedelta(years=60)):
            try:
                atributo = Atributo()
                atributo.individuo = instance
                atributo.tipo = TipoAtributo.objects.get(nombre__icontains='Poblacion de Riesgo')
            except TipoAtributo.DoesNotExist:
                print('No existe Atributo de Poblacion de Riesgo')
        #Situacion:
        situacion = Situacion()
        situacion.individuo = instance
        situacion.save()
        