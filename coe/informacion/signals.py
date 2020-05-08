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
from seguimiento.models import Seguimiento
#Imports de la app
from .models import Pasajero
from .models import Individuo, Domicilio, Situacion, Relacion
from .models import Atributo, SignosVitales, Documento

#Logger
logger = logging.getLogger('signals')

#Definimos nuestra señales
@receiver(post_save, sender=Individuo)
def estado_inicial(created, instance, **kwargs):
    if created:
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
        #Creamos inicializacion
        seguimiento = Seguimiento(individuo=instance)
        seguimiento.tipo = "I"
        seguimiento.aclaracion = "Ingreso al sistema"
        seguimiento.save()

@receiver(post_save, sender=Pasajero)
def relacion_vehiculo(created, instance, **kwargs):
    if created and (not instance.traslado.vehiculo.tipo == 1):
        for pasajero in instance.traslado.pasajeros.all().exclude(individuo__pk=instance.individuo.pk):
            relacion = Relacion()
            relacion.tipo = 'CE'
            relacion.individuo = instance.individuo
            relacion.relacionado = pasajero.individuo
            relacion.aclaracion = "Mismo Vehiculo-Mismo Traslado"
            relacion.save()

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
    if created and instance.ubicacion:#Si creamos nueva posicion
        individuo = instance.individuo
        #Creamos una nueva situacion
        if individuo.situacion_actual:
            situacion = individuo.situacion_actual
            situacion.pk = None
        else:
            situacion = Situacion(individuo=individuo)
            situacion.estado = 40
        situacion.conducta = 'E'
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
    if created:
        individuo = instance.individuo
        for relacion in individuo.relaciones.all():
            sit_rel = relacion.relacionado.situacion_actual
            if not sit_rel:#Si no tenia estado le creamos inicial
                sit_rel = Situacion()
                sit_rel.individuo = relacion.relacionado
                sit_rel.aclaracion = "Inicializado por el sistema"
                sit_rel.estado = 11
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
                sit_rel.aclaracion = "Detectado por sistema, Relacionado con: " + individuo.num_doc
                if sit_rel.estado > anterior_estado:
                    sit_rel.save()

@receiver(post_save, sender=Relacion)
def relacionar_situacion(created, instance, **kwargs):
    #Creamos la relacion inversa
    if created:
        individuo = instance.individuo
        if individuo.situacion_actual:
            situ_actual = individuo.situacion_actual
        else:
            sit = Situacion()
            sit.individuo = individuo
            sit.aclaracion = "Inicializada por Sistema"
            sit.save()
            situ_actual = sit
        #Obtenemos relacionado
        relacionado = instance.relacionado
        #Si no tenia le creamos
        if not relacionado.situacion_actual:
            sit = Situacion()
            sit.individuo = relacionado
            sit.aclaracion = "Inicializada por Sistema"
            sit.save()
            relacionado = Individuo.objects.get(pk=relacionado.id)
        if situ_actual.estado > relacionado.situacion_actual.estado:
            sit = Situacion()
            sit.individuo = relacionado
            sit.conducta = 'C'
            if situ_actual.estado == 32:#Contacto Alto Riesgo            
                sit.estado = 31
            if situ_actual.estado == 40:#Sospechoso
                sit.estado = 32
                sit.conducta = 'D'
            if situ_actual.estado == 50:#Confirmado
                sit.estado = 40
                sit.conducta = 'D'
            sit.aclaracion = "Relacion Detectada por el sistema"
            sit.save()

@receiver(post_save, sender=Atributo)
def iniciar_tracking_transportistas(created, instance, **kwargs):
    if created and instance.tipo == "CT":
        pass  #  INICIAMOS TRACKING DEL INDIVIDUO

#Creamos Seguimientos
@receiver(post_save, sender=Domicilio)
def poner_en_seguimiento(created, instance, **kwargs):
    if created and instance.aislamiento:
        atributo = Atributo(individuo=instance.individuo)
        atributo.tipo = 'VE'
        atributo.aclaracion = "Por Ingreso a Aislamiento."
        atributo.save()

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