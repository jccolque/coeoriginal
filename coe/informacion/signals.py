#Imports Python
import copy
import logging
#Imports Django
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models.signals import post_save, post_delete
#imports Extras
from dateutil.relativedelta import relativedelta
#Imports del proyecto
#Imports de la app
from seguimiento.models import Seguimiento
#from .models import Pasajero
from .models import Individuo, Domicilio, Situacion, Relacion
from .models import Atributo, SignosVitales, Documento
from .models import TrasladoVehiculo

#Logger
logger = logging.getLogger('signals')

#Definimos nuestra señales
@receiver(post_save, sender=Individuo)
def estado_inicial(created, instance, **kwargs):
    if created and not instance.situacion_actual:
        logger.info("Creamos a: " + str(instance))
        #Situacion Inicial:
        situacion = Situacion()
        situacion.individuo = instance
        situacion.aclaracion = "Iniciada por Sistema"
        situacion.save()
        #   Vejez +60 años
        if instance.fecha_nacimiento:
            if instance.fecha_nacimiento < (timezone.now().date() - relativedelta(years=60)):
                atributo = Atributo()
                atributo.individuo = instance
                atributo.tipo = 'PR'
                atributo.save()

#@receiver(post_save, sender=TrasladoVehiculo)
#def relacion_vehiculo(instance, **kwargs):
#    if not instance.traslado.vehiculo.tipo == 1:
#        for pasajero in instance.pasajeros.exclude(pk=instance.individuo.pk):
#            relacion = Relacion()
#            relacion.tipo = 'CE'
#            relacion.individuo = instance.individuo
#            relacion.relacionado = pasajero.individuo
#            relacion.aclaracion = "Mismo Vehiculo-Mismo Traslado"
#            relacion.save()

@receiver(post_save, sender=Domicilio)
def domicilio_actual(created, instance, **kwargs):
    if created:
        individuo = instance.individuo
        individuo.domicilio_actual = instance
        individuo.save()

@receiver(post_save, sender=Domicilio)
def relacion_domicilio(created, instance, **kwargs):
    if created and not instance.aislamiento:#Que no sea sitio de aislamiento
        domicilios = Domicilio.objects.filter(
                        localidad=instance.localidad,
                        calle=instance.calle,
                        numero=instance.numero,
                        aislamiento=False
                    ).exclude(
                        individuo=instance.individuo
                    )#Excluyendolo a el
        if domicilios.count() < 8:#Para evitar super relaciones por error
            for domicilio in domicilios:
                #Evitamos repetir relaciones
                try:
                    relacion = Relacion.objects.get(individuo=instance.individuo, relacionado=domicilio.individuo)
                    relacion.aclaracion = relacion.aclaracion + " - Mismo Domicilio(AutoDetectado)"
                    relacion.save()
                except Relacion.DoesNotExist:
                    relacion = Relacion()
                    relacion.tipo = 'MD'
                    relacion.individuo = instance.individuo
                    relacion.relacionado = domicilio.individuo
                    relacion.aclaracion = instance.calle + ' ' + instance.numero
                    relacion.save()

#Evolucionamos Estado segun Domicilio
@receiver(post_save, sender=Domicilio)
def aislar_individuo(created, instance, **kwargs):
    if created and instance.ubicacion:#Si lo mandamos a aislamiento
        individuo = instance.individuo
        #Obtenemos situacion actual
        situacion_actual = individuo.get_situacion()
        #Si no esta en aislamiento
        if situacion_actual.conducta not in ('D', 'E'):
            situacion = Situacion(individuo=individuo)
            situacion.conducta = 'E'
            situacion.fecha = instance.fecha
            situacion.aclaracion = "Aislado por traslado a ubicacion de Aislamiento/Internacion"
            situacion.save()

@receiver(post_save, sender=Relacion)
def crear_relacion_inversa(created, instance, **kwargs):
    #Creamos la relacion inversa
    if created and not instance.inversa():
        relacion = Relacion()
        relacion.tipo = instance.tipo
        relacion.individuo = instance.relacionado
        relacion.relacionado = instance.individuo
        relacion.aclaracion = instance.aclaracion
        relacion.save()

@receiver(post_delete, sender=Relacion)
def eliminar_relacion_inversa(instance, **kwargs):
    #Eliminamos relacion inversa
    inversa = instance.inversa()
    if inversa:
        inversa.delete()

@receiver(post_save, sender=Situacion)
def situacion_actual(created, instance, **kwargs):
    if created:
        individuo = instance.individuo
        individuo.situacion_actual = instance
        individuo.save()

#Evolucionamos Estado segun relaciones
@receiver(post_save, sender=Situacion)
def afectar_relacionados(created, instance, **kwargs):
    individuo = instance.individuo
    for relacion in individuo.relaciones.all():
        #Obtenemos la situacion
        sit_rel = relacion.relacionado.get_situacion()
        #Procesamos lo que nos importa
        if instance.estado > sit_rel.estado and sit_rel.estado > 2:#Que sea peor y que no este fuera de provincia o muerto...
            anterior_estado = copy.copy(sit_rel.estado)
            #Tramos situacion actual del relacionado
            sit_rel.id = None
            #Generamos situ nueva segun caso
            if instance.estado == 32:#Contacto Alto Riesgo            
                sit_rel.estado = 31
            if instance.estado == 40:#Sospechoso
                sit_rel.estado = 32
            if instance.estado == 50:#Confirmado
                sit_rel.estado = 40
            #Agregamos descripcion y guardamos
            sit_rel.conducta = 'B'
            sit_rel.aclaracion = "Detectado por sistema, Relacionado con: " + str(individuo)
            if sit_rel.estado > anterior_estado:
                sit_rel.save()

@receiver(post_save, sender=Relacion)
def relacionar_situacion(created, instance, **kwargs):
    #Creamos la relacion inversa
    if created:
        individuo = instance.individuo
        sit_individuo = individuo.get_situacion()
        #Obtenemos relacionado
        relacionado = instance.relacionado
        #Si no tenia le creamos
        sit_relacionado = relacionado.get_situacion()
        #Chequeamos situaciones:
        if sit_individuo.estado > sit_relacionado.estado:
            if sit_individuo.estado == 32:#Contacto Alto Riesgo            
                sit_relacionado.estado = 31
            if sit_individuo.estado == 40:#Sospechoso
                sit_relacionado.estado = 32
            if sit_individuo.estado == 50:#Confirmado
                sit_relacionado.estado = 40
            sit_relacionado.aclaracion = "Situacion Escalada por Relacion Detectada por sistema"
            sit_relacionado.save()

@receiver(post_save, sender=Atributo)
def aislamiento_domiciliario(created, instance, **kwargs):
    if created and instance.tipo == "AD":
        #Creamos la situacion de aislamiento
        sit_actual = instance.individuo.get_situacion()
        if sit_actual.conducta not in ('D', 'E'):
            sit = Situacion()
            sit.individuo = instance.individuo
            sit.conducta = 'E'
            sit.aclaracion = "Debe Realizar Cuarentena Obligatoria en su Hogar"
            sit.save()
            #Lo asignamos a vigilancia epidemiologica
            atributo = Atributo()
            atributo.individuo = instance.individuo
            atributo.tipo = 'VE'
            atributo.aclaracion = "Por Ingreso a Aislamiento."
            atributo.save()

@receiver(post_save, sender=Situacion)
def quitar_vigilancia_confirmado(created, instance, **kwargs):
    if instance.estado == 50:
        if created or ('estado' in kwargs.get('update_fields')):#Si creamos o pasamos a confirmado
            seguimiento = Seguimiento(individuo=instance.individuo)
            seguimiento.tipo = 'FS'
            seguimiento.aclaracion = 'Fin de Seguimiento Normal por TEST Confirmado'
            seguimiento.save()

#@receiver(post_save, sender=Atributo)
#def iniciar_tracking_transportistas(created, instance, **kwargs):
#    if created and instance.tipo == "CT":
#        pass  #  INICIAMOS TRACKING DEL INDIVIDUO