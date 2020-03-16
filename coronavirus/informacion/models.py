#Imports de python

#Realizamos imports de Django
from django.db import models
from django.utils import timezone
#Imports de paquetes extras
from auditlog.registry import auditlog
from tinymce.models import HTMLField
#Imports del proyecto:
from core.choices import TIPO_DOCUMENTOS
from operadores.models import Operador
from georef.models import Localidad, Barrio
#Imports de la app
from .choices import TIPO_IMPORTANCIA, TIPO_ARCHIVO, TIPO_VEHICULO

#Tipo Definition
class TipoSintoma(models.Model):#Origen del Dato
    nombre = models.CharField('Nombre', max_length=100)
    descripcion = HTMLField(verbose_name='Plan de Ruta')
    importancia = models.IntegerField(choices=TIPO_IMPORTANCIA, default='1')
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
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'tipo': self.get_tipo_display(),
            'nombre': self.nombre,
            'archivo': self.archivo,
            'fecha': self.fecha,
            'operador': self.operador,
            'procesado': self.procesado,
        }

class Vehiculo(models.Model):
    tipo = models.IntegerField(choices=TIPO_VEHICULO, default='1')
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    identificacion = models.CharField('Identificacion Patente/Codigo', max_length=200)
    cant_pasajeros = models.IntegerField(default='1')
    empresa = models.CharField('Empresa (Si aplica)', max_length=200, null=True, blank=True)
    plan = HTMLField(verbose_name='Plan de Ruta')
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.identificacion
    def as_dict(self):
        return {
            'id': self.id,
            'tipo': self.get_tipo_display(),
            'fecha': self.fecha,
            'identificacion': self.identificacion,
            'cant_pasajeros': self.cant_pasajeros,
            'empresa': self.empresa,
            'plan': self.plan,
        }

class Individuo(models.Model):
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.IntegerField('Numero de Documento/Pasaporte', unique=True)
    apellidos = models.CharField('Apellidos', max_length=100)
    nombres = models.CharField('Nombres', max_length=100)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    telefono = models.CharField('Telefono', max_length=20, default='+549388', null=True, blank=True)
    email = models.EmailField('Correo Electronico', null=True, blank=True)#Enviar mails
    nacionalidad = models.CharField('Apellidos', max_length=100)
    origen = models.CharField('Apellidos', max_length=200)
    destino = models.CharField('Apellidos', max_length=200)
    particularidades = HTMLField(null=True, blank=True)
    def __str__(self):
        return str(self.num_doc) + ': ' + self.apellidos + ', ' + self.nombres
    def as_dict(self):
        return {
            'id': self.id,
            'tipo_doc': self.get_tipo_doc_display(),
            'num_doc': self.num_doc,
            'apellidos': self.apellidos,
            'nombres': self.nombres,
            'fecha_nacimiento': self.fecha_nacimiento,
            'telefono': self.telefono,
            'email': self.email,
            'nacionalidad': self.nacionalidad,
            'origen': self.origen,
            'destino': self.destino,
            'particularidades': self.particularidades,
        }

class Domicilio(models.Model):
    individuo = models.OneToOneField(Individuo, on_delete=models.CASCADE, related_name="domicilio")
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="domicilios_individuos")
    barrio = models.ForeignKey(Barrio, on_delete=models.SET_NULL, null=True, blank=True, related_name="domicilios_individuos")
    calle = models.CharField('Calle', max_length=50, default='', blank=False)
    numero = models.CharField('Numero', max_length=50, default='', blank=False)
    def __str__(self):
        return self.calle + ' ' + self.numero + ', ' + str(self.localidad)
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "localidad": str(self.localidad),
            "barrio": str(self.barrio),
            "calle": self.calle,
            "numero": self.numero,
        }

class Origen(models.Model):#Origen del Dato
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="origenes")
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="origenes")
    def __str__(self):
        return str(self.vehiculo) + ': ' + str(self.individuo)
    def as_dict(self):
        return {
            "id": self.id,
            "vehiculo_id": self.vehiculo.id,
            "individuo_id": self.individuo.id,
        }

class Sintoma(models.Model):#Origen del Dato
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="sintomas")
    sintoma = models.ForeignKey(TipoSintoma, on_delete=models.CASCADE, related_name="sintomas")
    aclaracion =  models.CharField('Aclracion', max_length=200)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    def __str__(self):
        return str(self.sintoma) + ': ' + str(self.fecha)
    def as_dict(self):
        return {
            "id": self.id,
            "individuo_id": self.individuo.id,
            "sintoma_id": self.sintoma.id,
            "aclaracion": self.aclaracion,
            "fecha": self.fecha,
        }

#Auditoria
auditlog.register(Archivo)
auditlog.register(Vehiculo)
auditlog.register(Individuo)
auditlog.register(Origen)
auditlog.register(Sintoma)