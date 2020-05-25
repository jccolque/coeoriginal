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
from operadores.models import Operador
from core.choices import TIPO_DOCUMENTOS, TIPO_SEXO
from georef.models import Nacionalidad, Localidad
#Imports de la app
from informacion.choices import TIPO_DOCUMENTO
from informacion.models import Individuo
from .choices import TIPO_REFERENCIA, TIPO_ORGANIZACION, TIPO_CONFIRMA, ESTADO_PEDIDO
from .tokens import token_provision


# Create your models here.
class Organization(models.Model):
    cuit = models.CharField('CUIT', max_length=13, unique=True)
    denominacion = models.CharField('Razon Social', max_length=100)
    tipo_organizacion = models.CharField('Tipo de Organizacion', choices=TIPO_ORGANIZACION, max_length=5, default='ONG')
    fecha_constitucion = models.DateField(verbose_name="Fecha de Constitucion", null=True, blank=True)
    mail_institucional = models.EmailField(verbose_name="MAIL INSTITUCIONAL", null=True, blank=True)#Enviar mails
    telefono_inst1 = models.CharField('Telefono Fijo Institucional 1', max_length=50, default='+549388', null=True, blank=True)
    telefono_inst2 = models.CharField('Telefono Fijo Institucional 2', max_length=50, default='+549388', null=True, blank=True)
    celular_inst1 = models.CharField('Celular Institucional 1', max_length=50, default='+549388', null=True, blank=True)
    celular_inst2 = models.CharField('Celular Institucional 2', max_length=50, default='+549388', null=True, blank=True)
    archivo_adjunto = models.FileField('Documentación Respaldatoria de la Organización', upload_to='permisos/organizacion', null=True, blank=True)
    descripcion = models.CharField('Descripcion del Objeto Social', max_length=1000, default='', blank=False)    
    def __str__(self):
        return str(self.cuit) + ': ' + self.denominacion
    def get_foto(self):
        if self.archivo_adjunto:
            return self.archivo_adjunto.url
        else:
            return NOIMAGE
    def as_dict(self):
        return {
            'id': self.id,
            'cuit': self.cuit,
            'tipo_organizacion': self.get_tipo_organizacion_display(),
            'fecha_constitucion': str(self.fecha_constitucion),
            'mail_institucional': self.mail_institucional,
            'telefono_inst1': self.telefono_inst1,
            'telefono_inst2': self.telefono_inst2,
            'celular_inst1': self.celular_inst1,
            'celular_inst2': self.celular_inst2,
            'descripcion': self.descripcion,
        }
    def localidad(self):
        if self.domicilio:
            return self.domicilio.localidad
        else:
            return None

class Responsable(models.Model):
    organizacion = models.OneToOneField(Organization, on_delete=models.CASCADE)    
    apellidos = models.CharField('Apellidos', max_length=100)
    nombres = models.CharField('Nombres', max_length=100)
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.CharField('Número de Documento/Pasaporte', 
        max_length=50,
        validators=[RegexValidator('^[A-Z_\d]*$', 'Solo Mayusculas.')],
        unique=True,
    )
    cuil = models.CharField('CUIL', max_length=13)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)
    tipo_cond = models.CharField('Condicion Poblacional', choices=TIPO_REFERENCIA, max_length=4, default='N')
    rol = models.CharField('Rol Institucional', max_length=100)
    mail = models.EmailField('Email', null=True, blank=True)#Enviar mails
    telefono1 = models.CharField('Telefono Fijo 1', max_length=50, default='+549388', null=True, blank=True)
    telefono2 = models.CharField('Telefono Fijo 2', max_length=50, default='+549388', null=True, blank=True)
    celular1 = models.CharField('Celular 1', max_length=50, default='+549388', null=True, blank=True)
    celular2 = models.CharField('Celular 2', max_length=50, default='+549388', null=True, blank=True)
    #Funciones
    def __str__(self):
        return str(self.num_doc) + ': ' + self.apellidos + ', ' + self.nombres 

#Datos de la organizacion que pide coca
class Domic_o(models.Model):
    organizacion = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="pedidos_org", null=True, blank=True)
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="domic_org")
    calle = models.CharField('Calle', max_length=200, null=True, blank=True)
    numero = models.CharField('Numero', max_length=100, null=True, blank=True)
    barrio = models.CharField('Barrio', max_length=200, null=True, blank=True)
    manzana = models.CharField('Manzana', max_length=200, null=True, blank=True)
    lote = models.CharField('Barrio', max_length=200, null=True, blank=True)
    piso = models.CharField('Departamento-Piso', max_length=200, null=True, blank=True)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)  
   
    class Meta:
        ordering = ['fecha', ]
    def __str__(self):
        return self.calle + ' ' + self.numero + ', ' + str(self.localidad.nombre)
    def nombre_corto(self):
        return self.calle + ' ' + self.numero + ', ' + self.localidad.nombre
    def as_dict(self):
        return {
            "id": self.id,
            "organizacion_id": self.organizacion.id,
            "localidad": str(self.localidad),
            "calle": self.calle,
            "numero": self.numero,
            "barrio": self.barrio,
            "manzana": self.manzana,
            "lote": self.lote,
            "piso": self.piso
        }

class Empleado(models.Model):
    organizacion = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="org_empleados")   
    apellidos = models.CharField('Apellidos', max_length=100)
    nombres = models.CharField('Nombres', max_length=100)
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.CharField('Número de Documento/Pasaporte', 
        max_length=50,
        validators=[RegexValidator('^[A-Z_\d]*$', 'Solo Mayusculas.')],
        unique=True,
    )
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento", null=True, blank=True)
    mail = models.EmailField('Email', null=True, blank=True)#Enviar mails
    def __str__(self):
        return str(self.num_doc) + ': ' + self.apellidos + ', ' + self.nombres 

class Peticionp(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="pedidos_personas")
    destino = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="pedidosd_personas")
    email_contacto = models.EmailField('Correo Electrónico de Contacto', max_length=200)
    cantidad = models.CharField('Cantidad de Coca (en gramos)', max_length=50)    
    #Interno
    token = models.CharField('Token', max_length=50, default=token_provision, unique=True)
    fecha = models.DateTimeField('Fecha de registro', default=timezone.now)
    estado = models.CharField('Estado', choices=ESTADO_PEDIDO, max_length=1, default='C')
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="provisiones")
    #Aclaraciones
    aclaracion = HTMLField('Aclaraciones', null=True)    
    def __str__(self):
        return self.email_contacto + self.cantidad

class Emails_Peticionp(models.Model):
    peticion = models.ForeignKey(Peticionp, on_delete=models.CASCADE, related_name="emails")
    fecha = models.DateTimeField('Fecha de Envio', default=timezone.now)
    asunto = models.CharField('Asunto', max_length=100)
    cuerpo = models.CharField('Cuerpo', max_length=1000)
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="peticion_emailsenviados")

