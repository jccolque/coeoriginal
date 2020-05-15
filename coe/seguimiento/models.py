#Import de python
from datetime import timedelta
#Imports Django
from django.db import models
from django.utils import timezone
#Imports Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import LOADDATA
from operadores.models import Operador
from informacion.models import Individuo
#Imports de la app
from .choices import TIPO_SEGUIMIENTO, TIPO_VIGIA

# Create your models here.
class Seguimiento(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="seguimientos")
    tipo = models.CharField('Tipo Seguimiento', choices=TIPO_SEGUIMIENTO, max_length=2, default='I')
    aclaracion = HTMLField()
    fecha = models.DateTimeField('Fecha del Seguimiento', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return str(self.fecha)[0:16] + ': ' + self.get_tipo_display() + ': ' + self.aclaracion

class Vigia(models.Model):
    tipo = models.CharField('Tipo Vigia', choices=TIPO_VIGIA, max_length=1, default='E')
    operador = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name="vigia")
    max_controlados = models.SmallIntegerField('Cantidad Maxima de Seguidos', default=60)
    controlados = models.ManyToManyField(Individuo, related_name='vigiladores')
    def __str__(self):
        return str(self.operador.nombres) + ' ' + str(self.operador.apellidos)
    def alertas_activas(self):
        limite = timezone.now() - timedelta(hours=12)
        return sum([1 for c in self.controlados.all() if c.seguimiento_actual and c.seguimiento_actual.fecha < limite])

if not LOADDATA:
    #Auditoria
    auditlog.register(Seguimiento)
    auditlog.register(Vigia)