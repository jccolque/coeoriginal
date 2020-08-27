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
    def icono(self):
        icono = "/img/icons/maps/house_red.png"
        #Por tipo
        if self.tipo == 'AD':#Si es autodiagnostico
            icono = "/img/icons/maps/autodiagnostico.png"
        elif self.tipo == 'TS':
            icono = "/img/icons/maps/test.png"
        elif self.tipo == 'ST':#Si inicio el tracking
            icono = "/img/icons/maps/house_red.png"
        elif self.tipo == 'PC':#Si es el origen de control
            icono = "/img/icons/maps/house.png"
        elif self.tipo == 'RG':#Si es un tracking
            icono = "/img/icons/maps/steps.png"
        elif self.tipo == 'CG':
            icono = "/img/icons/maps/detective.png"
        #Por alerta
        if self.alerta != 'SA':
            if self.tipo == 'RG':
                icono = "/img/icons/maps/alerta.png"
            if self.procesada:
                if self.tipo == 'CG':
                    icono = "/img/icons/maps/detective_red.png"
                else:
                    icono = "/img/icons/maps/alerta_procesada.png"
        #Devolvemos el icono correspondiente
        return icono

class GeOperador(models.Model):
    operador = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name="geoperador")
    max_controlados = models.SmallIntegerField('Cantidad Maxima de Controlados', default=30)
    controlados = models.ManyToManyField(Individuo, related_name='geoperadores')
    def __str__(self):
        return str(self.operador.nombres) + ' ' + str(self.operador.apellidos)
    def cantidad_controlados(self):
        return sum([1 for c in self.controlados.all()])
    def cap_disponible(self):
        return self.max_controlados - self.cantidad_controlados()
    def alertas_activas(self):
        total = 0#utilizamos este metodo por optimizacion
        for controlado in self.controlados.all():
            for geopos in controlado.geoposiciones.all():
                if geopos.alerta != 'SA' and not geopos.procesada:
                    total += 1
                    break
        return total
    def add_trackeado(self, individuo):
        #registro para auditoria
        history = HistTrackeados(individuo=individuo)
        history.geoperador = self
        history.evento = 'A'
        history.save()
        #agregamos:
        self.controlados.add(individuo)
    def del_trackeado(self, individuo):
        if individuo in self.controlados.all():
            #registro para auditoria
            history = HistTrackeados(individuo=individuo)
            history.geoperador = self
            history.evento = 'E'
            history.save()
            #eliminamos:
            self.controlados.remove(individuo)

class HistTrackeados(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="histgeotrackings")
    geoperador = models.ForeignKey(GeOperador, on_delete=models.SET_NULL, null=True, blank=True, related_name="histgeotrackings")
    evento = models.CharField('Tipo Vigia', choices=[('A', 'Asignacion'), ('E', 'Eliminacion')], max_length=2, default='A')
    fecha = models.DateTimeField('Fecha Registro', default=timezone.now)
    def __str__(self):
        return str(self.individuo) + ': ' + str(self.fecha) + ' para ' + self.get_evento_display() + '(Vigilante: ' + str(self.geoperador) + ')'

if not LOADDATA:
    #Auditoria
    auditlog.register(GeoPosicion)
    auditlog.register(GeOperador)
    auditlog.register(HistTrackeados)