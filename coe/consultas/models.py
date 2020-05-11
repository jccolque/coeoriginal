#Imports de Django
from django.db import models
#Imports Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import LOADDATA
from operadores.models import Operador

# Create your models here.
class Consulta(models.Model):
    autor = models.CharField('Nombre y Apellido', max_length=100)
    email = models.EmailField('Correo Electronico')
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

if not LOADDATA:
    #Auditoria
    auditlog.register(Consulta)
    auditlog.register(Respuesta)