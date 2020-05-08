#Imports Python
#Imports Django
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports Extras
#Imports del proyecto
#Imports de la app
from .models import Seguimiento

@receiver(post_save, sender=Seguimiento)
def seguimiento_actual(created, instance, **kwargs):
    if created:
        individuo = instance.individuo
        individuo.seguimiento_actual = instance
        individuo.save()

@receiver(post_save, sender=Seguimiento)
def descartar_sospechoso(created, instance, **kwargs):
    #Eliminamos relacion inversa
    if created and instance.tipo == "DT":
        situacion = Situacion()
        situacion.individuo = instance.individuo
        #El estado pasa a asintomatico
        if instance.individuo.situacion_actual:#Si tenia conducta actual
            situacion.conducta = instance.individuo.situacion_actual.conducta
        situacion.aclaracion = 'Descartado' + instance.aclaracion
        situacion.save()
