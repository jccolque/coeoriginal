#Imports Python
import logging
import traceback
#Imports Django
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Count
#imports Extras
#Imports del proyecto
from seguimiento.models import Seguimiento
#Imports de la app
from .models import GeoPosicion, GeOperador

#Logger
logger = logging.getLogger('signals')

#Definimos nuestra señales
@receiver(post_save, sender=GeoPosicion)
def asignar_geoperador(created, instance, **kwargs):
    if created and instance.tipo == 'ST':#Si lo ingresamos al sistema
        try:
            #Chequeamos que este en aislamiento
            if instance.individuo.situacion_actual.conducta in ('D', 'E'): 
                #Obtenemos el que menos controlados tiene
                geoperador = GeOperador.objects.annotate(cantidad=Count('controlados')).order_by('cantidad').first()
                #Se lo agregamos
                geoperador.controlados.add(instance.individuo)
        except:
            logger.info("Falla: No se pudo asignar Operador!")
            logger.info("Falla: "+str(traceback.format_exc()))

@receiver(post_save, sender=GeoPosicion)
def asignar_punto_control(created, instance, **kwargs):
    if created and instance.tipo == 'ST':#Si lo ingresamos al sistema
        try:
            #Chequeamos que este en aislamiento
            individuo = instance.individuo
            domicilio = individuo.domicilio_actual
            if domicilio.ubicacion:#Si es un alojamiento
                if domicilio.ubicacion.latitud and domicilio.ubicacion.longitud:#si definieron gps
                    geopos = GeoPosicion(individuo=individuo)
                    geopos.tipo = 'PC'
                    geopos.latitud = domicilio.ubicacion.latitud
                    geopos.longitud = domicilio.ubicacion.longitud
                    geopos.aclaracion = "Asignado Automaticamente: " + domicilio.ubicacion.nombre
                    geopos.save()
        except:
            logger.info("Falla: No se pudo asignar PC!")
            logger.info("Falla: "+str(traceback.format_exc()))

@receiver(post_save, sender=GeoPosicion)
def inicio_seguimiento(created, instance, **kwargs):
    if created and instance.tipo == 'ST':#Si lo ingresamos al sistema
        seguimiento = Seguimiento(individuo=instance.individuo)
        seguimiento.tipo = 'IT'
        seguimiento.aclaracion = "Autogenerado por Pulsera Activada"
        seguimiento.save()