#Imports Python
from django.db.models import Q
#Imports Django
from django.core.cache import cache
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports del proyecto
#Imports de la app
from .models import Origen
from .models import Individuo, Situacion, Relacion, Seguimiento
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

@receiver(post_save, sender=Origen)
def relacion_vehiculo(created, instance, **kwargs):
    if created:
        origenes = Origen.objects.filter(vehiculo=instance.vehiculo)
        for individuo in [o.individuo for o in origenes]:
            relacion = Relacion()
            relacion.tipo = 'CE'
            relacion.individuo = instance.individuo
            relacion.relacionado = individuo
            relacion.aclaracion = "Viajo en el mismo Vehiculo"
            relacion.save()

@receiver(post_save, sender=Relacion)
def invertir_relacion(created, instance, **kwargs):
    #Creamos la relacion inversa
    if created and not instance.inversa():
        relacion = Relacion()
        relacion.tipo = instance.tipo
        relacion.individuo = instance.relacionado
        relacion.relacionado = instance.individuo
        relacion.aclaracion = instance.aclaracion
        relacion.save()
    #Aca deberiamos meterle atributos a partir de origen > destino

@receiver(post_save, sender=Atributo)
def poner_en_seguimiento(created, instance, **kwargs):
    #Aca deberiamos meterle atributos a partir de origen > destino
    if created:
        print(instance.tipo.nombre)
        if "vigilancia" in instance.tipo.nombre.lower():
            seguimiento = Seguimiento()
            seguimiento.individuo = instance.individuo
            seguimiento.aclaracion = "Agregado Atributo en el sistema"
            seguimiento.save()
