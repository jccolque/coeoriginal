#Imports Python

#Imports Django
from django.db.models import Q
from django.core.cache import cache
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports Extras
from dateutil.relativedelta import relativedelta
#Imports de la app
from .models import Origen
from .models import Individuo, Domicilio, Situacion, Relacion, Seguimiento
from .models import Atributo, TipoAtributo

#Definimos nuestra señales
@receiver(post_save, sender=Individuo)
def estado_inicial(created, instance, **kwargs):
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
                atributo.newtipo = 'PR'
                atributo.save()
            except TipoAtributo.DoesNotExist:
                print('No existe Atributo de Poblacion de Riesgo')

@receiver(post_save, sender=Origen)
def relacion_vehiculo(created, instance, **kwargs):
    if created:
        origenes = Origen.objects.filter(control=instance.control)
        for individuo in [o.individuo for o in origenes]:
            relacion = Relacion()
            relacion.tipo = 'CE'
            relacion.individuo = instance.individuo
            relacion.relacionado = individuo
            relacion.aclaracion = "Mismo Vehiculo-Mismo Control"
            relacion.save()

@receiver(post_save, sender=Domicilio)
def relacion_domicilio(created, instance, **kwargs):
    if created:
        domicilios = Domicilio.objects.filter(
            localidad=instance.localidad,
            calle=instance.calle,
            numero=instance.numero,
        )
        domicilios = domicilios.exclude(individuo=instance.individuo)
        for domicilio in domicilios:
            #Evitamos repetir relaciones
            try:
                relacion = Relacion.objects.get(tipo='CE', individuo=instance.individuo, relacionado=domicilio.individuo)
                relacion.aclaracion = "Mismo Domicilio"
                relacion.save()
            except Relacion.DoesNotExist:
                relacion = Relacion()
                relacion.tipo = 'CE'
                relacion.individuo = instance.individuo
                relacion.relacionado = domicilio.individuo
                relacion.aclaracion = "Mismo Domicilio"
                relacion.save()
        #Los que estan a menos de 100 metros
        #Hasta no acomodar la DB esto no se puede hacer

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

@receiver(post_save, sender=Relacion)
def relacionar_situacion(created, instance, **kwargs):
    #Creamos la relacion inversa
    if created:
        individuo = instance.individuo
        situ_actual = individuo.situacion_actual()
        relacionado = instance.relacionado
        if situ_actual.estado > relacionado.situacion_actual().estado:
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
def poner_en_seguimiento(created, instance, **kwargs):
    if created:
        if "vigilancia" in instance.tipo.nombre.lower():
            seguimiento = Seguimiento()
            seguimiento.individuo = instance.individuo
            seguimiento.aclaracion = "Agregado Atributo en el sistema"
            seguimiento.save()

#Evolucionamos Estado segun relaciones
@receiver(post_save, sender=Situacion)
def afectar_situacion(created, instance, **kwargs):
    if created:
        individuo = instance.individuo
        for relacion in individuo.relaciones.all():
            sit = relacion.relacionado.situacion_actual()
            if not sit:#Si no tenia estado le creamos inicial
                sit = Situacion()
                sit.individuo = relacion.relacionado
                sit.aclaracion = "Inicializado por el sistema"
                sit.estado = 1
            #Procesamos lo que nos importa
            if instance.estado > sit.estado:
                #Tramos situacion actual del relacionado
                sit.id = None
                #Generamos situ nueva segun caso
                if instance.estado == 32:#Contacto Alto Riesgo            
                    sit.estado = 31
                if instance.estado == 40:#Sospechoso
                    sit.estado = 32
                if instance.estado == 50:#Confirmado
                    sit.estado = 32
                #Agregamos descripcion y guardamos
                sit.conducta = 'B'
                sit.aclaracion = "Detectado por sistema, Relacionado con: " + individuo.num_doc
                sit.save()