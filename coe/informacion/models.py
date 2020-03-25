#Imports de python

#Realizamos imports de Django
from django.db import models
from django.utils import timezone
#Imports de paquetes extras
from auditlog.registry import auditlog
from tinymce.models import HTMLField
from django.core.validators import RegexValidator
#Imports del proyecto:
from core.choices import TIPO_DOCUMENTOS, TIPO_SEXO
from operadores.models import Operador
from georef.models import Nacionalidad, Localidad
#Imports de la app
from .choices import TIPO_IMPORTANCIA, TIPO_ARCHIVO
from .choices import TIPO_VEHICULO, TIPO_ESTADO, TIPO_CONDUCTA
from .choices import TIPO_RELACION, TIPO_SEGUIMIENTO
from .choices import TIPO_ATRIBUTO, TIPO_SINTOMA

#Tipo Definition
class TipoAtributo(models.Model):#Origen del Dato
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    importancia = models.IntegerField(choices=TIPO_IMPORTANCIA, default='1')
    class Meta:
        ordering = ['nombre']
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'importancia': self.get_importancia_display(),
        }

class TipoSintoma(models.Model):#Origen del Dato
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = HTMLField(verbose_name='Descripcion', null=True, blank=True)
    importancia = models.IntegerField(choices=TIPO_IMPORTANCIA, default='1')
    class Meta:
        ordering = ['nombre']
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'importancia': self.get_importancia_display(),
        }

# Create your models here.
class Archivo(models.Model):
    tipo = models.IntegerField(choices=TIPO_ARCHIVO, default='1')
    nombre = models.CharField('Nombres', max_length=100)
    archivo = models.FileField('Archivo', upload_to='informacion/')
    fecha = models.DateTimeField('Fecha del evento', default=timezone.now)
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="archivos")
    procesado = models.BooleanField(default=False)
    descripcion = HTMLField(verbose_name='Descripcion', null=True, blank=True)
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'tipo': self.get_tipo_display(),
            'nombre': self.nombre,
            'archivo': str(self.archivo),
            'fecha': str(self.fecha),
            'operador': str(self.operador),
            'procesado': self.procesado,
        }

class Enfermedad(models.Model):#Origen del Dato
    nombre = models.CharField('Nombre', max_length=100)
    descripcion = HTMLField(verbose_name='Descripcion', null=True, blank=True)
    importancia = models.IntegerField(choices=TIPO_IMPORTANCIA, default='1')
    sintomas = models.ManyToManyField(TipoSintoma)
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'importancia': self.get_importancia_display(),
        }


#Vehiculos
class Vehiculo(models.Model):
    tipo = models.IntegerField(choices=TIPO_VEHICULO, default='1')
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    identificacion = models.CharField('Identificacion Patente/Codigo', max_length=200, unique=True)
    empresa = models.CharField('Empresa (Si aplica)', max_length=200, null=True, blank=True)
    plan = HTMLField(verbose_name='Plan de Ruta', null=True, blank=True)
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.identificacion
    def as_dict(self):
        return {
            'id': self.id,
            'tipo': self.get_tipo_display(),
            'fecha': str(self.fecha),
            'identificacion': self.identificacion,
            'cant_pasajeros': self.cant_pasajeros,
            'empresa': self.empresa,
            'plan': self.plan,
        }

#Individuos
class Individuo(models.Model):
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.CharField('Numero de Documento/Pasaporte', 
        max_length=50,
        validators=[RegexValidator('^[A-Z_\d]*$', 'Solo Mayusculas.')],
        unique=True,
    )
    sexo = models.CharField('Sexo', max_length=1, choices=TIPO_SEXO, default='M')
    apellidos = models.CharField('Apellidos', max_length=100)
    nombres = models.CharField('Nombres', max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)
    telefono = models.CharField('Telefono', max_length=50, default='+549388', null=True, blank=True)
    email = models.EmailField('Correo Electronico', null=True, blank=True)#Enviar mails
    nacionalidad = models.ForeignKey(Nacionalidad, on_delete=models.CASCADE, related_name="individuos")
    origen = models.ForeignKey(Nacionalidad, on_delete=models.CASCADE, null=True, blank=True, related_name="individuos_origen")
    destino = models.ForeignKey(Localidad, on_delete=models.CASCADE, null=True, blank=True, related_name="individuos_destino")
    observaciones = HTMLField(null=True, blank=True)
    def __str__(self):
        return str(self.num_doc) + ': ' + self.apellidos + ', ' + self.nombres
    def as_dict(self):
        return {
            'id': self.id,
            'tipo_doc': self.get_tipo_doc_display(),
            'num_doc': self.num_doc,
            'apellidos': self.apellidos,
            'nombres': self.nombres,
            'fecha_nacimiento': str(self.fecha_nacimiento),
            'telefono': self.telefono,
            'email': self.email,
            'nacionalidad': self.nacionalidad,
            'origen': self.origen,
            'destino': self.destino,
            'observaciones': self.observaciones,
        }
    def situacion_actual(self):
        if self.situaciones.all():
            return [s for s in self.situaciones.all()][-1]
        else:
            return None
    def domicilio_actual(self):
        if self.domicilios.all():
            return [d for d in self.domicilios.all()][-1]
        else:
            return None
    def localidad_actual(self):
        if self.domicilio_actual():
            return self.domicilio_actual().localidad
        else:
            return None
    def ultimo_seguimiento(self):
        if self.seguimientos.all():
            return self.seguimientos.last()
        else:
            return None

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
    def as_dict(self):
        return {
            "tipo": self.get_tipo_display(),
            "individuo_id": self.individuo.id,
            "relacionado_id": self.relacionado.id,
            "aclaracion": self.aclaracion,
            "fecha": str(self.fecha),
        }
    def inversa(self):
        try:
            return Relacion.objects.get(tipo=self.tipo, individuo=self.relacionado, relacionado=self.individuo)
        except Relacion.DoesNotExist:
            return None

#Relacion vehicular
class ControlVehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="controles")
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    def __str__(self):
        return self.aclaracion + ': ' + str(self.fecha)
    def as_dict(self):
        return {
            'id': self.id,
            'vehiculo_id': self.vehiculo.id,
            'vehiculo': str(self.vehiculo),
            'aclaracion': self.aclaracion,
            'fecha': str(self.fecha),
        }    

class Origen(models.Model):#Origen del Dato
    control = models.ForeignKey(ControlVehiculo, on_delete=models.CASCADE, related_name="origenes")
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="origenes")
    def __str__(self):
        return str(self.control) + ': ' + str(self.individuo)
    def as_dict(self):
        return {
            "id": self.id,
            "control_id": self.control.id,
            "individuo_id": self.individuo.id,
        }

class Domicilio(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="domicilios")
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="domicilios_individuos")
    calle = models.CharField('Calle', max_length=100, default='', blank=False)
    numero = models.CharField('Numero', max_length=100, default='', blank=False)
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return self.calle + ' ' + self.numero + ', ' + str(self.localidad)
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "localidad": str(self.localidad),
            "calle": self.calle,
            "numero": self.numero,
        }

class GeoPosicion(models.Model):
    domicilio = models.OneToOneField(Domicilio, on_delete=models.CASCADE, related_name="geoposicion")
    latitud = models.DecimalField('latitud', max_digits=12, decimal_places=10)
    longitud = models.DecimalField('longitud', max_digits=12, decimal_places=10)
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    def __str__(self):
        return str(self.domicilios) + ': ' + str(self.latitud) + '|' + str(self.longitud)
    def as_dict(self):
        return {
            "id": self.id,
            "domicilio_id": self.domicilio.id,
            "latitud": str(self.latitud),
            "longitud": str(self.longitud),
            "aclaracion": self.aclaracion,
            "fecha": str(self.fecha),
        }

class Situacion(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="situaciones")
    estado = models.IntegerField('Estado de Seguimiento', choices=TIPO_ESTADO, default=1)
    conducta = models.CharField('Conducta', max_length=1, choices=TIPO_CONDUCTA, default='A')
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return self.get_estado_display() + '-'  + self.get_conducta_display()
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "estado_id": self.estado,
            "estado": self.get_estado_display(),
            "conducta_id": self.conducta,
            "conducta": self.get_conducta_display(),
            "fecha": str(self.fecha),
        }

class Atributo(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="atributos")
    tipo = models.ForeignKey(TipoAtributo, on_delete=models.CASCADE, related_name="atributos")
    newtipo = models.CharField('Tipo', choices=TIPO_ATRIBUTO, max_length=2, null=True)
    aclaracion =  models.CharField('Aclaracion', max_length=200, null=True, blank=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    activo = models.BooleanField(default=True)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return str(self.individuo) + ': ' + str(self.tipo) + ' ' + str(self.fecha)
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "tipo_id": self.tipo.id,
            "tipo": str(self.tipo),
            "aclaracion": self.aclaracion,
            "fecha": str(self.fecha),
            "activo": self.activo,
        }

class Sintoma(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="sintomas")
    tipo = models.ForeignKey(TipoSintoma, on_delete=models.CASCADE, related_name="sintomas")
    newtipo = models.CharField('Tipo', choices=TIPO_SINTOMA, max_length=3, null=True)
    aclaracion =  models.CharField('Aclaracion', max_length=200, null=True, blank=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return str(self.tipo) + ': ' + str(self.fecha)
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "tipo_id": self.tipo.id,
            "tipo": str(self.tipo),
            "aclaracion": self.aclaracion,
            "fecha": str(self.fecha),
        }

class Seguimiento(models.Model):
    tipo = models.CharField('Tipo Seguimiento', choices=TIPO_SEGUIMIENTO, max_length=1, default='I')
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="seguimientos")
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Seguimiento', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return str(self.fecha)[0:16] + ': ' + self.get_tipo_display() + ': ' + self.aclaracion
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "tipo_id": self.tipo,
            "aclaracion": self.aclaracion,
            "fecha": str(self.fecha),
        }

#Señales
from .signals import estado_inicial
from .signals import invertir_relacion
from .signals import relacion_vehiculo
from .signals import relacion_domicilio
from .signals import poner_en_seguimiento
from .signals import afectar_situacion
#Auditoria
auditlog.register(Archivo)
auditlog.register(Vehiculo)
auditlog.register(Individuo)
auditlog.register(Origen)
auditlog.register(Sintoma)