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
from .choices import TIPO_SEGUIMIENTO

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
    operador = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name="vigia")
    controlados = models.ManyToManyField(Individuo, related_name='vigiladores')
    def __str__(self):
        return str(self.operador.nombres) + ' ' + str(self.operador.apellidos)
    def alertas_activas(self):
        limite = timezone.now() - timedelta(hours=12)
        return self.controlados.exclude(seguimientos__fecha__gt=limite).count()

if not LOADDATA:
    #Auditoria
    auditlog.register(Seguimiento)
    auditlog.register(Vigia)
    #Señales
    from .signals import seguimiento_actual