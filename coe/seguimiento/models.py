#Import de python
from datetime import datetime, timedelta
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
from informacion.functions import actualizar_individuo
from geotracking.models import GeoPosicion
from georef.models import Localidad
#Imports de la app
from .choices import TIPO_SEGUIMIENTO, TIPO_VIGIA, ESTADO_OPERATIVO, ESTADO_RESULTADO
from .choices import TIPO_TURNO
from .choices import NIVEL_CONTENCION, NIVEL_ALIMENTOS, NIVEL_MEDICACION
from .choices import ESTADO_TIPO, TIPO_PRIORIDAD, TIPO_RESULTADO


# Create your models here.
class Seguimiento(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="seguimientos")
    tipo = models.CharField('Tipo Seguimiento', choices=TIPO_SEGUIMIENTO, max_length=2, default='I')
    aclaracion = HTMLField()
    fecha = models.DateTimeField('Fecha del Seguimiento', default=timezone.now)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="seguimientos_informados")
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return str(self.fecha)[0:16] + ': ' + self.get_tipo_display() + ': ' + self.aclaracion

class Condicion(models.Model):
    individuo = models.OneToOneField(Individuo, on_delete=models.CASCADE, related_name="condicion")
    contencion = models.SmallIntegerField('Contencion Familiar', choices=NIVEL_CONTENCION, default=0)
    alimentos = models.SmallIntegerField('Soporte Alimenticio', choices=NIVEL_ALIMENTOS, default=0)
    medicamentos = models.SmallIntegerField('Medicacion', choices=NIVEL_MEDICACION, default=0)
    atendido = models.BooleanField('Atendido', default=False)
    aclaracion = HTMLField()
    fecha = models.DateTimeField('Fecha del Informe', default=timezone.now)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="condiciones_informadas")
    def prioridad(self):
        dias = (timezone.now() - self.fecha).days
        return self.contencion + self.alimentos + self.medicamentos + dias

class Vigia(models.Model):
    tipo = models.CharField('Tipo Vigia', choices=TIPO_VIGIA, max_length=2, default='VE')
    aclaracion = models.CharField('Aclaraciones', max_length=200, null=True, blank=True)
    operador = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name="vigia")
    max_controlados = models.SmallIntegerField('Cantidad Maxima de Seguidos', default=60)
    priorizar = models.BooleanField('Priorizar Confirmados', default=False)
    controlados = models.ManyToManyField(Individuo, related_name='vigiladores')
    activo = models.BooleanField('Disponible', default=True)
    def __str__(self):
        return str(self.operador.nombres) + ' ' + str(self.operador.apellidos)
    def alertas_activas(self):
        limite = timezone.now() - timedelta(hours=12)
        return sum([1 for c in self.controlados.all() if c.seguimiento_actual and c.seguimiento_actual.fecha < limite])
    def cap_disponible(self):
        return self.max_controlados - sum([1 for c in self.controlados.all()])

#OPERATIVO
class OperativoVehicular(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="operativos")
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    cazadores = models.ManyToManyField(Individuo, related_name='cazadores360')
    estado = models.CharField(choices=ESTADO_OPERATIVO, max_length=1, default='C')#Al activarse > Prende Gps de todos los cazadores
    fecha_inicio = models.DateTimeField('Fecha Inicio del Operativo', null=True, blank=True)
    fecha_final = models.DateTimeField('Fecha Final del Operativo', null=True, blank=True)
    def __str__(self):
        return str(self.vehiculo) + ': ' + self.aclaracion
    def get_geoposiciones(self):
        ids = [c.id for c in self.cazadores.all()]
        geoposiciones = GeoPosicion.objects.filter(individuo__id__in=ids)
        #Filtramos por el tiempo que duro el operativo
        geoposiciones = geoposiciones.filter(fecha__gt=self.fecha_inicio)
        if self.fecha_final:
            geoposiciones = geoposiciones.filter(fecha__lt=self.fecha_final)
        return geoposiciones

class TestOperativo(models.Model):#cada test realizado
    operativo = models.ForeignKey(OperativoVehicular, on_delete=models.CASCADE, related_name="tests")
    num_doc = models.CharField('Numero de Documento/Pasaporte', 
        max_length=50,
        validators=[RegexValidator('^[A-Z_\d]*$', 'Solo Mayusculas.')],
    )
    individuo = models.ForeignKey(Individuo, on_delete=models.SET_NULL, null=True, blank=True, related_name="tests_aleatorios")
    geoposicion = models.ForeignKey(GeoPosicion, on_delete=models.SET_NULL, null=True, blank=True, related_name="tests_aleatorios")
    resultado = models.CharField(choices=ESTADO_RESULTADO, max_length=1, default='E')#Al activarse > Prende Gps de todos los cazadores
    fecha = models.DateTimeField('Fecha del Test', default=timezone.now)

class DatosGis(models.Model):
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="Localidades")    
    turno = models.CharField('Turno', choices=TIPO_TURNO, max_length=1)
    fecha_carga = models.DateTimeField('Fecha de Carga', default=timezone.now)
    confirmados = models.CharField('Casos Confirmados', max_length=5)   
    recuperados = models.CharField('Casos Recuperados', max_length=5)
    fallecidos = models.CharField('Fallecidos', max_length=5)
    pcr = models.CharField('Cantidad de PCR', max_length=5)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="datos_gis")
    def save(self):
        self.confirmados = self.confirmados.upper()
        self.recuperados = self.recuperados.upper()
        self.fallecidos = self.fallecidos.upper()
        self.pcr = self.pcr.upper()
        super(DatosGis, self).save()


class Muestra(models.Model):
    seguimiento = models.OneToOneField(Seguimiento, on_delete=models.CASCADE, related_name="muestra")
    fecha_muestra = models.DateField('Fecha de Muestra', default=timezone.now)
    estado = models.CharField('Estado', max_length=2, choices=ESTADO_TIPO, default='EE')
    prioridad = models.CharField('Prioridad', max_length=2, choices=TIPO_PRIORIDAD, default='SP')
    resultado = models.CharField('Resultado', max_length=2, choices=TIPO_RESULTADO, default='SR')
    grupo_etereo = models.CharField('Grupo Etereo', max_length=20)
    lugar_carga = models.CharField('Lugar de Carga', max_length=100, null = True, blank = True)
    #Sobreescribo el método save y guardo los campos mencionados en mayusculas
    def save(self):#innecesario
        self.estado = self.estado.upper()
        self.prioridad = self.prioridad.upper()
        self.resultado = self.resultado.upper()       
        super(Muestra, self).save()

if not LOADDATA:
    #Auditoria
    auditlog.register(Seguimiento)
    auditlog.register(Condicion)
    auditlog.register(Vigia)
    auditlog.register(DatosGis)
    auditlog.register(Muestra)