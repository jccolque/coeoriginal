#Import de python
from datetime import timedelta
#Imports Django
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
#Imports Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import LOADDATA
from operadores.models import Operador
from informacion.models import Individuo, Vehiculo
from geotracking.models import GeoPosicion
#Imports de la app
from .choices import TIPO_SEGUIMIENTO, TIPO_VIGIA, ESTADO_OPERATIVO, ESTADO_RESULTADO

# Create your models here.
class Seguimiento(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="seguimientos")
    tipo = models.CharField('Tipo Seguimiento', choices=TIPO_SEGUIMIENTO, max_length=2, default='I')
    aclaracion = HTMLField()
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="seguimientos")
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

class OperativoVehicular(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="operativos")
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    cazadores = models.ManyToManyField(Individuo, related_name='cazadores360')
    estado = models.CharField(choices=ESTADO_OPERATIVO, max_length=1, default='C')#Al activarse > Prende Gps de todos los cazadores
    fecha_inicio = models.DateTimeField('Fecha Inicio del Operativo', null=True, blank=True)
    fecha_final = models.DateTimeField('Fecha Final del Operativo', null=True, blank=True)
    def __str__(self):
        return str(self.vehiculo) + ': ' + self.aclaracion

class TestOperativo(models.Model):#cada test realizado
    operativo = models.ForeignKey(OperativoVehicular, on_delete=models.CASCADE, related_name="tests")
    num_doc = models.CharField('Numero de Documento/Pasaporte', 
        max_length=50,
        validators=[RegexValidator('^[A-Z_\d]*$', 'Solo Mayusculas.')],
        unique=True,
    )
    individuo = models.ForeignKey(Individuo, on_delete=models.SET_NULL, null=True, blank=True, related_name="tests_aleatorios")
    geoposicion = models.ForeignKey(GeoPosicion, on_delete=models.SET_NULL, null=True, blank=True, related_name="tests_aleatorios")
    resultado = models.CharField(choices=ESTADO_RESULTADO, max_length=1, default='E')#Al activarse > Prende Gps de todos los cazadores
    fecha = models.DateTimeField('Fecha del Test', default=timezone.now)

if not LOADDATA:
    #Auditoria
    auditlog.register(Seguimiento)
    auditlog.register(Vigia)