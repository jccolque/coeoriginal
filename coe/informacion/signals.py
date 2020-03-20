#Imports Python
from django.db.models import Q
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
        #Situacion Inicial:
        situacion = Situacion()
        situacion.individuo = instance
        situacion.save()
        #   Vejez +60 años
        if instance.fecha_nacimiento < (timezone.now().date() - relativedelta(years=60)):
            try:
                atributo = Atributo()
                atributo.individuo = instance
                atributo.tipo = TipoAtributo.objects.get(
                    Q(nombre__icontains='poblacion') & 
                    Q(nombre__icontains='riesgo')
                )
                atributo.save()
            except TipoAtributo.DoesNotExist:
                print('No existe Atributo de Poblacion de Riesgo')