#Imports de Python
import logging
import traceback
from datetime import timedelta
#Imports django
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
#Imports Extras
from background_task import background
#Imports del proyeco
#Import de la app
from inscripciones.models import Inscripcion

def continuar_inscripcion():
    inscriptos = Inscripcion.objects.filter(valido=True, tipo_inscripto='VS')
    total = inscriptos.count()
    print("Tenemos " + str(total) + " Inscriptos que comunicar.")
    index = 0
    for inscripto in inscriptos:
        index += 1
        to_email = inscripto.individuo.email
        #Preparamos el correo electronico
        mail_subject = 'COE2020 - Voluntariado Social'
        message = render_to_string('emails/continuar_inscripcion.html', {
                'inscripto': inscripto,
            })
        #Instanciamos el objeto mail con destinatario
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        print("Enviamos mail a: " + str(inscripto.individuo) + "(" + str(index) + "/" + str(total) + ")")