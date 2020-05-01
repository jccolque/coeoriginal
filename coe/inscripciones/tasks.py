#Imports de Python
import logging
from datetime import timedelta
#Imports django
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
#Imports Extras
from background_task import background
#Imports del proyeco
from coe.settings import SEND_MAIL
#Import de la app
from .models import Inscripcion

#Definimos logger
logger = logging.getLogger("tasks")

#Definimos tareas
@background(schedule=75)
def reintentar_validar():
    if SEND_MAIL:
        limite = timezone.now() - timedelta(days=4)
        inscriptos = Inscripcion.objects.filter(valido=False, fecha__gt=limite)
        for inscripto in inscriptos:
            to_email = inscripto.individuo.email
            #Preparamos el correo electronico
            mail_subject = 'Reintento de Validacion - Inscripcion al COE2020'
            message = render_to_string('emails/acc_active_inscripcion_social.html', {
                    'inscripto': inscripto,
                })
            #Instanciamos el objeto mail con destinatario
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()