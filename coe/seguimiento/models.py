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
from .choices import TIPO_SEGUIMIENTO, TIPO_VIGIA
from .choices import ESTADO_OPERATIVO, ESTADO_RESULTADO
from .choices import TIPO_TURNO
from .choices import NIVEL_CONTENCION, NIVEL_ALIMENTOS, NIVEL_MEDICACION
from .choices import ESTADO_TIPO, TIPO_PRIORIDAD, TIPO_RESULTADO

# Create your models here.
class Seguimiento(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="seguimientos")
    tipo = models.CharField('Tipo Seguimiento', choices=TIPO_SEGUIMIENTO, max_length=2, default='I', db_index=True)
    aclaracion = HTMLField()
    fecha = models.DateTimeField('Fecha del Seguimiento', default=timezone.now, db_index=True)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="seguimientos_informados")
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return str(self.fecha)[0:16] + ': ' + self.get_tipo_display() + ': ' + self.aclaracion
    def desde(self):
        return int((timezone.now() - self.fecha).total_seconds() / 3600)

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
    def add_vigilado(self, individuo):
        #registro para auditoria
        history = HistVigilancias(individuo=individuo)
        history.vigia = self
        history.evento = 'A'
        history.save()
        #agregamos:
        self.controlados.add(individuo)
    def del_vigilado(self, individuo):
        if individuo in self.controlados.all():
            #registro para auditoria
            history = HistVigilancias(individuo=individuo)
            history.vigia = self
            history.evento = 'E'
            history.save()
            #eliminamos:
            self.controlados.remove(individuo)
    def alertas_activas(self):
        limite = timezone.now() - timedelta(hours=12)
        return sum([1 for c in self.controlados.all() if c.seguimiento_actual and c.seguimiento_actual.fecha < limite])
    def cap_disponible(self):
        return self.max_controlados - sum([1 for c in self.controlados.all()])

class Configuracion(models.Model):
    vigia = models.OneToOneField(Vigia, on_delete=models.CASCADE, related_name="configuracion")
    alerta_verde = models.IntegerField('Alerta Verde', default=16)
    alerta_amarilla = models.IntegerField('Alerta Amarilla', default=24)
    alerta_roja = models.IntegerField('Alerta Roja', default=36)
    def __str__(self):
        return str(self.alerta_verde)+'/'+str(self.alerta_amarilla)+'/'+str(self.alerta_roja)

class HistVigilancias(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="vigilancias")
    vigia = models.ForeignKey(Vigia, on_delete=models.SET_NULL, null=True, blank=True, related_name="vigilancias")
    evento = models.CharField('Tipo Vigia', choices=[('A', 'Asignacion'), ('E', 'Eliminacion')], max_length=2, default='A')
    fecha = models.DateTimeField('Fecha Registro', default=timezone.now)
    def __str__(self):
        return str(self.individuo) + ': ' + str(self.fecha) + ' para ' + self.get_evento_display() + '(Vigilante: ' + str(self.vigia) + ')'

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
    def ultima_intervencion(self):
        intervenciones = [i for i in self.individuo.seguimientos.all() if i.tipo == "T"]
        if intervenciones:
            return intervenciones[-1]

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
    #Llaves foraneas
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="muestras", null=True, blank=True)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, related_name="operadores_muestras", null=True, blank=True)
    #Campos propios
    fecha_muestra = models.DateField('Fecha de Muestra', default=timezone.now)
    estado = models.CharField('Estado', max_length=2, choices=ESTADO_TIPO, default='EE')
    prioridad = models.CharField('Prioridad', max_length=2, choices=TIPO_PRIORIDAD, default='SP')
    resultado = models.CharField('Resultado', max_length=2, choices=TIPO_RESULTADO, default='SR')
    grupo_etereo = models.CharField('Grupo Etereo', max_length=200, null=True, blank=True)
    lugar_carga = models.CharField('Lugar de Carga', max_length=100, null = True, blank = True)
    edad = models.CharField('Edad', max_length=200, null=True, blank=True)
    #Sobreescribo el método save y guardo los campos mencionados en mayusculas
    def save(self):#innecesario
        self.estado = self.estado.upper()
        self.prioridad = self.prioridad.upper()
        self.resultado = self.resultado.upper()       
        super(Muestra, self).save()

#if not LOADDATA:
    #Auditoria
auditlog.register(Seguimiento)
auditlog.register(Condicion)
auditlog.register(Vigia)
auditlog.register(Configuracion)
auditlog.register(HistVigilancias)
auditlog.register(DatosGis)
auditlog.register(Muestra)