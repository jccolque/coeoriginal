#Imports de python
#Imports django
from django.db import models
#Extra modules import
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import DEBUG
from operadores.models import Operador
#Imports de la app
from .choices import TIPO_LOG

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

class Consulta(models.Model):
    autor = models.CharField('Nombre y Apellido', max_length=100)
    email = models.EmailField('Correo Electronico Personal')
    telefono = models.CharField('Telefono', max_length=100, blank=True, null=True)
    asunto = models.CharField('Asunto', max_length=100)
    descripcion = HTMLField()
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    valida = models.BooleanField('Email Validado', default=False)
    respondida = models.BooleanField('Respondida', default=False)
    class Meta:
        ordering = ['fecha_consulta', ]
    def __str__(self):
        return self.autor + ": " + self.asunto + '(' + str(self.fecha_consulta.date()) + ')'

class Respuesta(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name="respuestas")
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="respuestas")
    respuesta = HTMLField()
    fecha = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.consulta) + ": " + self.respuesta

#Auditoria
auditlog.register(Faq)
#Señales
from core.signals import enviar_mail_new_user
