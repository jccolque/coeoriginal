#Imports Python
import string
import random
#Imports de Django
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
#Imports del proyecto
from coe.constantes import NOMAIL
from coe.settings import SEND_MAIL
#Imports de la app
from .tokens import account_activation_token

#Definimos nuestras señales
@receiver(post_save, sender=User)
def enviar_mail_new_user(instance, created, **kwargs):
    if SEND_MAIL:#Si esta habilitado el envio de mails
        if created and instance.email != NOMAIL:
            usuario = instance
            #Le generamos password y lo desactivamos para que active por mail
            raw_password = ''.join(random.sample(string.ascii_uppercase + string.digits, k=8))
            usuario.set_password(raw_password)
            usuario.is_active = False
            usuario.save()
            #enviar email de validacion
            to_email = usuario.email
            #Preparamos el correo electronico
            mail_subject = 'Bienvenido al Sistema Centralizado COE!'
            message = render_to_string('emails/acc_active_user.html', {
                    'usuario': usuario,
                    'raw_password': raw_password,
                    'token': account_activation_token.make_token(usuario),
                })
            #Instanciamos el objeto mail con destinatario
            email = EmailMessage(mail_subject, message, to=[to_email])
            #Enviamos el correo
            email.send()
