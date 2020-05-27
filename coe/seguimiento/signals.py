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
from informacion.models import Individuo, Domicilio
from informacion.models import Situacion, Atributo, SignosVitales, Documento
#Imports de la app
from .models import Seguimiento, Vigia
from .functions import crear_doc_descartado

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
    #Eliminamos relacion inversa
    if created and instance.tipo == "DT":
        situacion = Situacion(individuo=instance.individuo)
        #El estado pasa a asintomatico
        situacion.conducta = instance.individuo.get_situacion().conducta
        situacion.aclaracion = 'Descartado' + instance.aclaracion
        situacion.save()
        #Creamos archivo de Descartado por Test
        doc = Documento(individuo=instance.individuo)
        doc.tipo = 'TN'
        doc.archivo = crear_doc_descartado(doc.individuo)
        doc.aclaracion = "TEST NEGATIVO CONFIRMADO"
        doc.save()
        #Enviar mail
        to_email = instance.individuo.email
        #Preparamos el correo electronico
        mail_subject = 'Constancia de Test - COE2020'
        message = render_to_string('emails/constancia_test.html', {
                'individuo': instance.individuo,
                'doc': doc,
            })
        #Instanciamos el objeto mail con destinatario
        email = EmailMessage(mail_subject, message, to=[to_email])
        #Adjuntamos archivo
        #email.attach(doc.archivo)
        #email.add_attachment(doc.archivo.read(), maintype='application/pdf', subtype='pdf', filename='certificado.pdf')
        #Enviamos el correo
        email.send()

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
def buscar_controlador(created, instance, **kwargs):
    if created:
        #Si es vigilancia Epidemiologica
        if instance.tipo == 'VE':
            try:
                if not instance.individuo.vigiladores.filter(tipo='E').exists():
                    vigias = Vigia.objects.filter(tipo='E').annotate(cantidad=Count('controlados'))
                    for vigia in vigias.order_by('cantidad'):
                        if vigia.max_controlados > vigia.cantidad:
                            vigia.controlados.add(instance.individuo)
                            break#Lo cargamos, terminamos
            except:
                logger.info("No existen Vigias, " + str(instance.individuo) + " quedo sin vigilante.")
        #Si es Vigilancia de Salud Mental
        if instance.tipo == 'VM':
            try:
                if not instance.individuo.vigiladores.filter(tipo='M').exists():
                    vigias = Vigia.objects.filter(tipo='M').annotate(cantidad=Count('controlados'))
                    for vigia in vigias.order_by('cantidad'):
                        if vigia.max_controlados > vigia.cantidad:
                            vigia.controlados.add(instance.individuo)
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