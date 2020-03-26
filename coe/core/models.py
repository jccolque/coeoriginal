#Imports de python
#Imports django
from django.db import models
#Extra modules import
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from operadores.models import Operador

#Modelos
# Create your models here.
class Faq(models.Model):
    orden = models.IntegerField()
    pregunta = models.CharField('Titulo', max_length=200)
    respuesta = HTMLField()
    class Meta:
        ordering = ['orden', ]
    def __str__(self):
        return self.pregunta
    def as_dict(self):
        return {
            "id": int(self.id),
            "orden": int(self.orden),
            "pregunta": self.pregunta,
            "respuesta": self.respuesta,
        }

#Auditoria
auditlog.register(Faq)
#Señales
from core.signals import enviar_mail_new_user
