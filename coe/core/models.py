#Imports de python
#Imports django
from django.db import models
from django.utils import timezone
#Extra modules import
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import LOADDATA
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

class Aclaracion(models.Model):
    modelo = models.CharField('Modelo', max_length=200)
    descripcion = models.TextField('Descripcion')
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name='aclaraciones')

if not LOADDATA:
    #Auditoria
    auditlog.register(Faq)