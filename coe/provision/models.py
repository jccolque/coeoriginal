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
from .choices import TIPO_REFERENCIA, TIPO_ORGANIZACION


# Create your models here.

class Person(models.Model):    
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
    mail = models.EmailField('Email', null=True, blank=True)#Enviar mails
    telefono1 = models.CharField('Telefono Fijo 1', max_length=50, default='+549388', null=True, blank=True)
    telefono2 = models.CharField('Telefono Fijo 2', max_length=50, default='+549388', null=True, blank=True)
    celular1 = models.CharField('Celular 1', max_length=50, default='+549388', null=True, blank=True)
    celular2 = models.CharField('Celular 2', max_length=50, default='+549388', null=True, blank=True)
    #Funciones
    def __str__(self):
        return str(self.num_doc) + ': ' + self.apellidos + ', ' + self.nombres 


#Datos del individuo que pide coca
class Domic_p(models.Model):
    persona_pedido = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="pedidos_per")    
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="domic_per")
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

class Organization(models.Model):
    cuit = models.CharField('CUIT', max_length=13, unique=True,)
    denominacion = models.CharField('Razon Social', max_length=100)
    tipo_organizacion = models.CharField('Tipo de Organizacion', choices=TIPO_ORGANIZACION, max_length=5, default='ONG')
    fecha_constitucion = models.DateField(verbose_name="Fecha de Constitucion", null=True, blank=True)
    mail_institucional = models.EmailField(verbose_name="MAIL INSTITUCIONAL", null=True, blank=True)#Enviar mails
    telefono_inst1 = models.CharField('Telefono Fijo Institucional 1', max_length=50, default='+549388', null=True, blank=True)
    telefono_inst2 = models.CharField('Telefono Fijo Institucional 2', max_length=50, default='+549388', null=True, blank=True)
    celular_inst1 = models.CharField('Celular Institucional 1', max_length=50, default='+549388', null=True, blank=True)
    celular_inst2 = models.CharField('Celular Institucional 2', max_length=50, default='+549388', null=True, blank=True)
    archivo_adjunto = models.FileField('Documentación Respaldatorio de la Organización', upload_to='permisos/organizacion', null=True, blank=True)
    descripcion = models.CharField('Descripcion del Objeto Social', max_length=1000, default='', blank=False)    
    def __str__(self):
        return str(self.cuit) + ': ' + self.denominacion 


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
