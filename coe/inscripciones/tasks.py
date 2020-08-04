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
from coe.settings import SEND_MAIL
from background.functions import hasta_madrugada
#Import de la app
from .models import Inscripcion

#Definimos logger
logger = logging.getLogger("tasks")

#Definimos tareas
@background(schedule=hasta_madrugada(50))
def reintentar_validar():
    logger.info("\nInicia reintentar_validar")
    if SEND_MAIL:
        limite = timezone.now() - timedelta(days=3)
        inscriptos = Inscripcion.objects.filter(valido=False, fecha__gt=limite)
        for inscripto in inscriptos:
            logger.info("Procesamos a:" + str(inscripto.individuo))
            try:
                to_email = inscripto.individuo.email
                #Preparamos el correo electronico
                mail_subject = 'Reintento de Validacion - Inscripcion al COE2020'
                message = render_to_string('emails/acc_active_inscripcion_social.html', {
                        'inscripto': inscripto,
                    })
                #Instanciamos el objeto mail con destinatario
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
            except Exception as error:
                logger.info("Fallo revalidacion: "+str(error)+'\n'+str(traceback.format_exc()))
    
    #Damos de baja los que ya cumplieron 3 dias y no validaron
    inscriptos = Inscripcion.objects.filter(valido=False, fecha__lt=limite)
    inscriptos.update(estado=99)
    logger.info("Finaliza reintentar_validar\n")