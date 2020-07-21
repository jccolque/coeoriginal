#Imports Django
from django.db import models
from django.db.models import Q
from django.utils import timezone
#Imports Extras
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import LOADDATA
from operadores.models import Operador
from informacion.models import Individuo
#Imports de la app
from .choices import TIPO_GEOPOS, TIPO_ALERTA

# Create your models here.
class GeoPosicion(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="geoposiciones")
    tipo = models.CharField('Tipo GeoPosicion', max_length=2, choices=TIPO_GEOPOS, default='MS')
    latitud = models.DecimalField('latitud', max_digits=12, decimal_places=10)
    longitud = models.DecimalField('longitud', max_digits=12, decimal_places=10)
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    distancia = models.DecimalField('Distancia a Base', max_digits=8, decimal_places=2, default=0)
    alerta = models.CharField('Tipo de Alerta', choices=TIPO_ALERTA, max_length=2, default='SA')
    procesada = models.BooleanField('Procesada', default=False)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return str(self.latitud) + '|' + str(self.longitud)

class GeOperador(models.Model):
    operador = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name="geoperador")
    max_controlados = models.SmallIntegerField('Cantidad Maxima de Controlados', default=30)
    controlados = models.ManyToManyField(Individuo, related_name='geoperadores')
    def __str__(self):
        return str(self.operador.nombres) + ' ' + str(self.operador.apellidos)
    def controlados_actuales(self):
        return self.controlados.all()#Deberiamos filtrar
    def cantidad_controlados(self):
        return self.controlados_actuales().count()
    def alertas_activas(self):
        return self.controlados.filter(Q(geoposiciones__procesada=False) & ~Q(geoposiciones__alerta='SA')).distinct().count()

if not LOADDATA:
    #Auditoria
    auditlog.register(GeoPosicion)
    auditlog.register(GeOperador)