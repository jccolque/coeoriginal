#Imports Python
import logging
#Imports Django
from django.db.models import Count
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports Extras
#Imports del proyecto
from informacion.models import Individuo, Domicilio
from informacion.models import Situacion, Atributo, SignosVitales, Documento
#Imports de la app
from .models import Seguimiento

#Logger
logger = logging.getLogger('signals')

#Definimos señales
@receiver(post_save, sender=Individuo)
def iniciar_seguimiento(created, instance, **kwargs):
    if created and not instance.situacion_actual:
        #Creamos inicializacion
        seguimiento = Seguimiento(individuo=instance)
        seguimiento.tipo = "I"
        seguimiento.aclaracion = "Ingreso al sistema"
        seguimiento.save()

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
        situacion = Situacion(individuo=instance.individuo)
        #El estado pasa a asintomatico
        situacion.conducta = instance.individuo.get_situacion().conducta
        situacion.aclaracion = 'Descartado' + instance.aclaracion
        situacion.save()

@receiver(post_save, sender=Domicilio)
def poner_en_seguimiento(created, instance, **kwargs):
    if created and instance.aislamiento:
        individuo = instance.individuo
        #Generamos atributo de vigilancia
        atributo = Atributo(individuo=individuo)
        atributo.tipo = 'VE'
        atributo.aclaracion = "Por Ingreso a Aislamiento."
        atributo.save()
        #Lo ponemos en seguimiento:
        try:
            vigias = Vigia.objects.filter(tipo='S').annotate(cantidad=Count('controlados')).order_by('cantidad')
            for vigia in vigias:
                if vigia.max_controlados > vigia.controlados.count():
                    vigia.controlados.add(individuo)
                    break#Lo cargamos, terminamos
        except:
            logger.info("No existen Vigias, " + str(individuo) + " quedo sin vigilante.")

@receiver(post_save, sender=Atributo)
def seguimiento_mental(created, instance, **kwargs):
    if created and instance.tipo == 'VM':
        try:
            vigias = Vigia.objects.filter(tipo='M').annotate(cantidad=Count('controlados')).order_by('cantidad').first()
            for vigia in vigias:
                if vigia.max_controlados > vigia.controlados.count():
                    vigia.controlados.add(individuo)
                    break#Lo cargamos, terminamos
        except:
            logger.info("No existen Vigias, " + str(instance.individuo) + " quedo sin vigilante.")

@receiver(post_save, sender=SignosVitales)
def cargo_signosvitales(created, instance, **kwargs):
    if created:
        seguimiento = Seguimiento(individuo=instance.individuo)
        seguimiento.tipo = 'E'
        seguimiento.aclaracion = "Se Informaron Signos vitales"
        seguimiento.save()

@receiver(post_save, sender=Documento)
def cargo_documento(created, instance, **kwargs):
    if created:
        seguimiento = Seguimiento(individuo=instance.individuo)
        seguimiento.tipo = 'M'
        seguimiento.aclaracion = "Se Cargo Documento " + instance.get_tipo_display()
        seguimiento.save()