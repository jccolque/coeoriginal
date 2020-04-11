#Imports de python
import qrcode
#Realizamos imports de Django
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
#Imports de paquetes extras
from auditlog.registry import auditlog
from tinymce.models import HTMLField
#Imports del proyecto:
from coe.constantes import NOIMAGE
from coe.settings import MEDIA_ROOT
from operadores.models import Operador
from core.choices import TIPO_DOCUMENTOS, TIPO_SEXO
from georef.models import Nacionalidad, Localidad, Ubicacion
#Imports de la app
from .choices import TIPO_IMPORTANCIA, TIPO_ARCHIVO
from .choices import TIPO_VEHICULO, TIPO_ESTADO, TIPO_CONDUCTA
from .choices import TIPO_RELACION, TIPO_SEGUIMIENTO
from .choices import TIPO_ATRIBUTO, TIPO_SINTOMA
from .choices import TIPO_DOCUMENTO
from .choices import TIPO_PERMISO
from .choices import TIPO_TRIAJE

# Create your models here.
class Archivo(models.Model):
    tipo = models.IntegerField(choices=TIPO_ARCHIVO, default='1')
    nombre = models.CharField('Nombres', max_length=100)
    archivo = models.FileField('Archivo', upload_to='informacion/archivos/')
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
    #sintomas = models.ManyToManyField(TipoSintoma)
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
    conductor = models.CharField('Conductor:', max_length=200, null=True, blank=True)
    aclaracion = HTMLField(verbose_name='Aclaracion', null=True, blank=True)
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
    origen = models.ForeignKey(Nacionalidad, on_delete=models.SET_NULL, null=True, blank=True, related_name="individuos_origen")
    destino = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True, blank=True, related_name="individuos_destino")
    observaciones = HTMLField(null=True, blank=True)
    fotografia = models.FileField('Fotografia', upload_to='informacion/individuos/', null=True, blank=True)
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    #Actuales
    situacion_actual = models.OneToOneField('Situacion', on_delete=models.SET_NULL, related_name="situacion_actual", null=True, blank=True)
    domicilio_actual = models.OneToOneField('Domicilio', on_delete=models.SET_NULL, related_name="domicilio_actual", null=True, blank=True)
    #Funciones
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
    def ultimo_seguimiento(self):
        if self.seguimientos.all():
            return [d for d in self.seguimientos.all()][-1]
        else:
            return None
    def geoposicion(self):
        return self.geoposiciones.last()
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
    def get_foto(self):
        if self.fotografia:
            return self.fotografia.url
        else:
            return NOIMAGE
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
    def seguimiento(self):
        return self.geoposiciones.filter(aclaracion="INICIO TRACKING").exists()

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

#Datos del individuo
class Domicilio(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="domicilios")
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="domicilios_individuos")
    calle = models.CharField('Calle', max_length=200)
    numero = models.CharField('Numero', max_length=100)
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='')
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    aislamiento = models.BooleanField('Separado/Aislamiento', default=False)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, related_name="aislados", null=True, blank=True)
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
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="geoposiciones")
    latitud = models.DecimalField('latitud', max_digits=12, decimal_places=10)
    longitud = models.DecimalField('longitud', max_digits=12, decimal_places=10)
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    distancia = models.DecimalField('Distancia a Base', max_digits=8, decimal_places=2, default=0)
    alerta = models.BooleanField('Posicion de Alerta', default=False)
    def __str__(self):
        return str(self.latitud) + '|' + str(self.longitud)
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "latitud": str(self.latitud),
            "longitud": str(self.longitud),
            "aclaracion": self.aclaracion,
            "fecha": str(self.fecha),
        }

#Extras
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
    tipo = models.CharField('Tipo', choices=TIPO_ATRIBUTO, max_length=2, null=True)
    aclaracion =  models.CharField('Aclaracion', max_length=200, null=True, blank=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    activo = models.BooleanField(default=True)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return str(self.individuo) + ': ' + self.get_tipo_display() + ' ' + str(self.fecha)
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "tipo_id": self.tipo,
            "tipo": self.get_tipo_display(),
            "aclaracion": self.aclaracion,
            "fecha": str(self.fecha),
            "activo": self.activo,
        }

class Sintoma(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="sintomas")
    tipo = models.CharField('Tipo', choices=TIPO_SINTOMA, max_length=3, null=True)
    aclaracion =  models.CharField('Aclaracion', max_length=200, null=True, blank=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return self.get_tipo_display() + ': ' + str(self.fecha)
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "tipo_id": self.tipo,
            "tipo": self.get_tipo_display(),
            "aclaracion": self.aclaracion,
            "fecha": str(self.fecha),
        }

class Seguimiento(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="seguimientos")
    tipo = models.CharField('Tipo Seguimiento', choices=TIPO_SEGUIMIENTO, max_length=2, default='I')
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

class Documento(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="documentos")
    tipo = models.CharField('Tipo de Documento', choices=TIPO_DOCUMENTO, max_length=12, default='HM')
    archivo = models.FileField('Archivo', upload_to='informacion/individuo/documentos/')
    aclaracion = models.CharField('Aclaraciones', max_length=1000, default='', blank=False)
    fecha = models.DateTimeField('Fecha Subido', default=timezone.now)
    def __str__(self):
        return self.get_tipo_display()


#Apps Externas
class AppData(models.Model):
    individuo = models.OneToOneField(Individuo, on_delete=models.CASCADE, related_name="appdata")
    telefono = models.CharField('Telefono', max_length=50, default='+549388')
    email = models.EmailField('Correo Electronico', null=True, blank=True)#Enviar mails
    estado = models.CharField('Estado', choices=TIPO_TRIAJE, max_length=1, default='V')
    push_id = models.CharField('Push Notification ID', max_length=255, blank=True, null=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    def __str__(self):
        return str(self.individuo) + self.get_estado_display()

#Controles vehiculares
class TrasladoVehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="traslados")
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

class Pasajero(models.Model):
    traslado = models.ForeignKey(TrasladoVehiculo, on_delete=models.CASCADE, related_name="pasajeros")
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="pasajes")
    def __str__(self):
        return str(self.traslado) + ': ' + str(self.individuo)
    def as_dict(self):
        return {
            "id": self.id,
            "control_id": self.traslado.id,
            "individuo_id": self.individuo.id,
        }

#Permisos
class Permiso(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="permisos")
    tipo = models.CharField('Tipo Permiso', choices=TIPO_PERMISO, max_length=1, default='C')
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="permisos")
    begda = models.DateTimeField('Inicio Permiso', default=timezone.now)
    endda = models.DateTimeField('Fin Permiso', default=timezone.now)
    aclaracion = HTMLField(null=True, blank=True)
    def __str__(self):
        return self.get_tipo_display() + str(self.begda)[0:16]
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "tipo_id": self.tipo,
            "origen": self.origen,
            "destino": self.destino,
            "begda": str(self.fecha),
            "endda": str(self.fecha),
            "aclaracion": self.aclaracion,
        }
    def estado(self):
        if self.habilitado:
            return "Aprobado"
        else:
            return "En Espera"

#Señales
from .signals import estado_inicial
from .signals import poner_en_seguimiento
from .signals import situacion_actual
from .signals import domicilio_actual
from .signals import relacion_domicilio
from .signals import crear_relacion_inversa
from .signals import eliminar_relacion_inversa
from .signals import relacion_vehiculo
from .signals import relacionar_situacion
from .signals import afectar_relacionados
from .signals import aislados
from .signals import ocupar_capacidad_ubicacion
from .signals import recuperar_capacidad_ubicacion
from .signals import cargo_signosvitales
from .signals import cargo_documento

#Auditoria
auditlog.register(Archivo)
auditlog.register(Vehiculo)
auditlog.register(Individuo)
auditlog.register(TrasladoVehiculo)
auditlog.register(Sintoma)
auditlog.register(Permiso)