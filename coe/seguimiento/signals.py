#Imports Python
import logging
#Imports Django
from django.db.models import Count
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models.signals import post_save, post_delete
#imports Extras
#Imports del proyecto
from coe.settings import SEND_MAIL
from informacion.models import Individuo, Domicilio
from informacion.models import Situacion, Atributo, SignosVitales, Documento
#Imports de la app
from .models import Seguimiento, Vigia, TestOperativo
from .functions import crear_doc_descartado, asignar_vigilante 

#Logger
logger = logging.getLogger('signals')

#Definimos señales
@receiver(post_save, sender=Seguimiento)
def seguimiento_actual(created, instance, **kwargs):
    if created:
        individuo = instance.individuo
        individuo.seguimiento_actual = instance
        individuo.save()

@receiver(post_delete, sender=Seguimiento)
def recuperar_seguimiento(instance, **kwargs):
    individuo = instance.individuo
    individuo.seguimiento_actual = individuo.seguimientos.last()
    individuo.save()

@receiver(post_save, sender=Individuo)
def iniciar_seguimiento(created, instance, **kwargs):
    if created and not instance.situacion_actual:
        #Creamos inicializacion
        seguimiento = Seguimiento(individuo=instance)
        seguimiento.tipo = "I"
        seguimiento.aclaracion = "Ingreso al sistema"
        seguimiento.save()

@receiver(post_save, sender=Seguimiento)
def descartar_sospechoso(created, instance, **kwargs):
    if created and instance.tipo == "DT":
        #El estado pasa a asintomatico
        situacion = instance.individuo.get_situacion()
        situacion.estado = 10
        situacion.aclaracion = 'Descartado' + instance.aclaracion
        situacion.save()
        #Creamos archivo de Descartado por Test
        doc = Documento(individuo=instance.individuo)
        doc.tipo = 'TN'
        doc.archivo = crear_doc_descartado(doc.individuo)
        doc.aclaracion = "TEST NEGATIVO CONFIRMADO"
        doc.save()
        #Enviar mail
        if SEND_MAIL and instance.individuo.email:
            to_email = instance.individuo.email
            #Preparamos el correo electronico
            mail_subject = 'Constancia de Test - COE2020'
            message = render_to_string('emails/constancia_test.html', {
                    'individuo': instance.individuo,
                    'doc': doc,
                })
            #Instanciamos el objeto mail con destinatario
            email = EmailMessage(mail_subject, message, to=[to_email])
            #Enviamos el correo
            email.send()

@receiver(post_save, sender=Seguimiento)
def confirmar_sospechoso(created, instance, **kwargs):
    if created and instance.tipo == "CT":
        situacion = Situacion(individuo=instance.individuo)
        situacion.estado = 50
        situacion.conducta = 'E'
        situacion.aclaracion = "Confirmado por TEST PCR"
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

@receiver(post_save, sender=Atributo)
def atributo_vigilancia(created, instance, **kwargs):
    if created:
        #Si se indica alguna vigilancia
        if instance.tipo in ('VE', 'VM', 'VT', 'ST'):
            asignar_vigilante(instance.individuo, instance.tipo)

@receiver(post_save, sender=Seguimiento)
def quitar_seguimiento(created, instance, **kwargs):
    if created and instance.tipo == 'FS':
        instance.individuo.vigiladores.clear()

@receiver(post_save, sender=SignosVitales)
def cargo_signosvitales(created, instance, **kwargs):
    if created:
        seguimiento = Seguimiento(individuo=instance.individuo)
        seguimiento.tipo = 'E'
        seguimiento.aclaracion = "Se Informaron Signos vitales"
        seguimiento.save()

@receiver(post_save, sender=TestOperativo)
def test_get_individuo(created, instance, **kwargs):
    if created:
        try:
            instance.individuo = Individuo.objects.get(num_doc=instance.num_doc)
            instance.save()
        except:
            pass#No existe el individuo en el sistema