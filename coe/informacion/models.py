#Imports de python
import qrcode
import io
#Realizamos imports de Django
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
#Imports de paquetes extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto:
from coe.settings import BASE_DIR, STATIC_ROOT, MEDIA_ROOT, LOADDATA
from coe.constantes import NOIMAGE, DIAS_CUARENTENA
from core.choices import TIPO_DOCUMENTOS, TIPO_SEXO
from georef.models import Nacionalidad, Localidad, Ubicacion
from georef.functions import obtener_argentina
#Imports de la app
from .choices import TIPO_IMPORTANCIA, TIPO_ARCHIVO
from .choices import TIPO_VEHICULO, TIPO_ESTADO, TIPO_CONDUCTA
from .choices import TIPO_DOMICILIO
from .choices import TIPO_RELACION
from .choices import TIPO_ATRIBUTO, TIPO_SINTOMA, TIPO_PATOLOGIA
from .choices import TIPO_DOCUMENTO

# Create your models here.
class Archivo(models.Model):
    tipo = models.IntegerField(choices=TIPO_ARCHIVO, default='1')
    nombre = models.CharField('Nombres', max_length=100)
    archivo = models.FileField('Archivo', upload_to='informacion/archivos/')
    fecha = models.DateTimeField('Fecha del evento', default=timezone.now)
    procesado = models.BooleanField(default=False)
    descripcion = HTMLField(verbose_name='Descripcion', null=True, blank=True)
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.nombre

class Enfermedad(models.Model):#Origen del Dato
    nombre = models.CharField('Nombre', max_length=100)
    descripcion = HTMLField(verbose_name='Descripcion', null=True, blank=True)
    importancia = models.IntegerField(choices=TIPO_IMPORTANCIA, default='1')
    #sintomas = models.ManyToManyField(TipoSintoma)
    def __str__(self):
        return self.nombre

#Vehiculos
class Vehiculo(models.Model):
    tipo = models.IntegerField(choices=TIPO_VEHICULO, default='1')
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    identificacion = models.CharField('Identificacion Patente/Codigo', max_length=200, unique=True)
    empresa = models.CharField('Empresa (Si aplica)', max_length=200, null=True, blank=True)
    conductor = models.CharField('Conductor:', max_length=200, null=True, blank=True)
    aclaracion = HTMLField(verbose_name='Aclaracion', null=True, blank=True)
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.identificacion

#Individuos
class Individuo(models.Model):
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.CharField('Numero de Documento/Pasaporte', 
        max_length=50,
        validators=[RegexValidator('^[A-Z_\d]*$', 'Solo Mayusculas.')],
        unique=True,
    )
    apellidos = models.CharField('Apellidos', max_length=100)
    nombres = models.CharField('Nombres', max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)
    sexo = models.CharField('Sexo', max_length=1, choices=TIPO_SEXO, default='M')
    telefono = models.CharField('Telefono', max_length=50, default='+549388', null=True, blank=True)
    email = models.EmailField('Correo Electronico', null=True, blank=True)#Enviar mails
    nacionalidad = models.ForeignKey(Nacionalidad, on_delete=models.SET_NULL, null=True, blank=True, related_name="individuos")
    cuil = models.CharField('CUIL', max_length=13, null=True, blank=True)
    origen_internacional = models.ForeignKey(Nacionalidad, on_delete=models.SET_NULL, null=True, blank=True, related_name="individuos_origen")
    origen_nacional = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True, blank=True, related_name="individuos_origen")
    destino = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True, blank=True, related_name="individuos_destino")
    observaciones = HTMLField(null=True, blank=True)
    fotografia = models.FileField('Fotografia', upload_to='informacion/individuos/', null=True, blank=True)
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    #Actuales
    situacion_actual = models.OneToOneField('Situacion', on_delete=models.SET_NULL, related_name="situacion_actual", null=True, blank=True)
    domicilio_actual = models.OneToOneField('Domicilio', on_delete=models.SET_NULL, related_name="domicilio_actual", null=True, blank=True)
    seguimiento_actual = models.OneToOneField('seguimiento.Seguimiento', on_delete=models.SET_NULL, related_name="seguimiento_actual", null=True, blank=True)
    #Funciones
    def __str__(self):
        return str(self.num_doc) + ': ' + self.apellidos + ', ' + self.nombres
    def domicilio_origen(self):
        doms = [s.aclaracion for s in self.seguimientos.all() if s.tipo=='DF']
        if doms:
            return doms[-1]
    def domicilio_retorno(self):#El mas actualizado que no es de aislamiento
        doms = [d for d in self.domicilios.all() if d.ubicacion is None]
        if doms:
            return doms[-1]
    def domicilio_laboral(self):
        doms = [d for d in self.domicilios.all() if d.tipo=="LA"]
        if doms:
            return doms[-1]
    def geoposicion(self):
        geopos = self.geoposiciones.all()
        if geopos:
            return geopos[-1]
    def localidad_actual(self):
        if self.domicilio_actual:
            return self.domicilio_actual.localidad
        else:
            return None
    def get_situacion(self):
        if self.situacion_actual:
            return self.situacion_actual
        else:
            situacion = Situacion()
            situacion.individuo = self
            situacion.aclaracion = "Iniciada por Sistema"
            situacion.save()
            return situacion
    def aislado(self):
        sit = self.get_situacion()
        if sit.conducta in ('D', 'E'):
            return True
    def get_foto(self):
        if self.fotografia:
            return self.fotografia.url
        else:
            return NOIMAGE
    def get_permiso_nacional(self):
        return self.documentos.filter(tipo='PN').last()
    def get_qr(self):
        if self.qrpath:
            return self.qrpath
        else:
            path = MEDIA_ROOT + '/informacion/individuos/qrcode-'+ str(self.num_doc)+'.png'
            img = qrcode.make(str(self.id)+'-'+self.num_doc)
            img.save(path)
            relative_path = '/archivos/informacion/individuos/qrcode-'+ str(self.num_doc)+'.png'
            self.qrpath = relative_path
            self.save()
            return self.qrpath
    def get_dnis(self):
        return [doc for doc in self.documentos.all() if doc.tipo == 'DI']
    def tracking(self):
        return self.geoposiciones.exists()
    def dias_faltantes(self):
        sit = self.get_situacion()
        if sit.conducta in ('D', 'E'):
            return DIAS_CUARENTENA - (timezone.now() - self.situacion_actual.fecha).days
        else:
            return 'Sin Aislamiento'
    def ultima_alerta(self):
        alertas = [a for a in self.geoposiciones.all() if (a.alerta != "SA" and not a.procesada)]
        if alertas:
            return alertas[-1]
    def ultima_llamada(self):
        llamadas = [l for l in self.seguimientos.all() if l.tipo == "L"]
        if llamadas:
            return llamadas[-1]
    def controlador(self):
        return self.atributos.filter(tipo='CP').exists()
    def familiar(self):
        return self.relaciones.filter(tipo="F").last()
    def voluntario_autorizado(self):
        return self.documentos.filter(tipo='AT').last()
    def es_camionero(self):
        return True in [True for a in self.atributos.all() if a.tipo == 'VT']
    def tiene_obrasocial(self):
        return True in [True for a in self.atributos.all() if a.tipo == 'TO']
    def get_obrasocial(self):
        try:
            return self.atributos.filter(tipo='TO').last().aclaracion
        except:
            return "Sin obra social"

class Relacion(models.Model):#Origen del Dato
    tipo = models.CharField('Tipo Relacion', choices=TIPO_RELACION, max_length=2, default='F')
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="relaciones")
    relacionado = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="relacionado")
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    class Meta:
        unique_together = ['tipo', 'individuo', 'relacionado']
    def __str__(self):
        return str(self.individuo) + ' ' + self.get_tipo_display() + ' con ' + str(self.relacionado)
    def inversa(self):
        try:
            return Relacion.objects.get(tipo=self.tipo, individuo=self.relacionado, relacionado=self.individuo)
        except Relacion.DoesNotExist:
            return None

#Datos del individuo
class Domicilio(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="domicilios")
    tipo = models.CharField('Tipo Domicilio', choices=TIPO_DOMICILIO, max_length=2, default='HO')
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="domicilios_individuos")
    calle = models.CharField('Calle', max_length=200)
    numero = models.CharField('Numero', max_length=100)
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='')
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    #aislamiento = models.BooleanField('Separado/Aislamiento', default=False)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, related_name="aislados", null=True, blank=True)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return self.calle + ' ' + self.numero + ', ' + str(self.localidad.nombre)
    def nombre_corto(self):
        return self.calle + ' ' + self.numero + ', ' + self.localidad.nombre

#Extras
class Situacion(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="situaciones")
    estado = models.IntegerField('Estado de Seguimiento', choices=TIPO_ESTADO, default=11)
    conducta = models.CharField('Conducta', max_length=1, choices=TIPO_CONDUCTA, default='A')
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return self.get_estado_display() + '-'  + self.get_conducta_display()

class SignosVitales(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="signos_vitales")
    tension_sistolica = models.IntegerField('Tension Sistolica')
    tension_diastolica = models.IntegerField('Tension Diastolica')
    frec_cardiaca = models.IntegerField('Frecuencia Cardiaca')
    frec_respiratoria = models.IntegerField('Frecuencia Respiratoria')
    temperatura = models.DecimalField('Temperatura', max_digits=4, decimal_places=2)
    sat_oxigeno = models.IntegerField('Saturacion de Oxigeno')
    glucemia = models.IntegerField('Glucemia')
    observaciones = HTMLField(null=True, blank=True)
    fecha = models.DateTimeField('Fecha Subido', default=timezone.now)
    def __str__(self):
        return str(self.individuo) + ' de ' + str(self.fecha)

class Atributo(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="atributos")
    tipo = models.CharField('Tipo', choices=TIPO_ATRIBUTO, max_length=3, null=True)
    aclaracion =  models.CharField('Aclaracion', max_length=200, null=True, blank=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    activo = models.BooleanField(default=True)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return str(self.individuo) + ': ' + self.get_tipo_display() + ' ' + str(self.fecha)

class Sintoma(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="sintomas")
    tipo = models.CharField('Tipo', choices=TIPO_SINTOMA, max_length=3, null=True)
    aclaracion =  models.CharField('Aclaracion', max_length=200, null=True, blank=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return self.get_tipo_display() + ': ' + str(self.fecha)

class Patologia(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="patologias")
    tipo = models.CharField('Tipo', choices=TIPO_PATOLOGIA, max_length=3, null=True)
    codigo = models.CharField('Codigo', max_length=4, null=True, blank=True)
    aclaracion =  models.CharField('Aclaracion', max_length=200, null=True, blank=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return self.get_tipo_display() + ': ' + str(self.fecha)

class Documento(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="documentos")
    tipo = models.CharField('Tipo de Documento', choices=TIPO_DOCUMENTO, max_length=12, default='HM')
    archivo = models.FileField('Archivo', upload_to='informacion/individuos/documentos/')
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha Subido', default=timezone.now)
    activo = models.BooleanField(default=True)
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.aclaracion

#Controles vehiculares
class TrasladoVehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="traslados")
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    pasajeros = models.ManyToManyField(Individuo, related_name='traslados')
    def __str__(self):
        return self.aclaracion + ': ' + str(self.fecha)

if not LOADDATA:
    #Auditoria
    auditlog.register(Archivo)
    auditlog.register(Vehiculo)
    auditlog.register(Individuo)
    auditlog.register(Atributo)
    auditlog.register(Situacion)
    auditlog.register(SignosVitales)
    auditlog.register(Domicilio)
    auditlog.register(Documento)
    auditlog.register(Sintoma)
    auditlog.register(Patologia)
    auditlog.register(Relacion)
    auditlog.register(TrasladoVehiculo)
