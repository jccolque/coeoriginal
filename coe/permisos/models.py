#Imports de python
#Imports de django
from django.db import models
from django.utils import timezone
#Imports de paquetes extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from georef.models import Provincia, Localidad
from informacion.models import Individuo
#Imports de app
from .choices import TIPO_PERMISO
from .choices import TIPO_INGRESO, ESTADO_INGRESO
from .tokens import token_ingreso

# Create your models here.
class Permiso(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="permisos")
    tipo = models.CharField('Tipo Permiso', choices=TIPO_PERMISO, max_length=1, default='C')
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="permisos")
    begda = models.DateTimeField('Inicio Permiso', default=timezone.now)
    endda = models.DateTimeField('Fin Permiso', default=timezone.now)
    controlador = models.BooleanField(default=False)
    aclaracion = HTMLField(null=True, blank=True)
    def __str__(self):
        return self.get_tipo_display() + str(self.begda)[0:16]
    def estado(self):
        if self.endda > timezone.now():
            return "Activo"
        else:
            return "Vencido"

class IngresoProvincia(models.Model):
    tipo = models.CharField('Tipo Ingreso', choices=TIPO_INGRESO, max_length=1, default='P')
    email_contacto = models.EmailField('Correo Electronico de Contacto')
    fecha_llegada = models.DateTimeField('Fecha de Llegada', default=timezone.now)
    permiso_nacional = models.FileField('Permiso Nacional de Circulacion', upload_to='ingresos/')
    origen = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="ingresos")
    destino = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="ingresos")
    #Vehiculo
    marca = models.CharField('Marca del Vehiculo', max_length=200)
    modelo = models.CharField('Modelo del Vehiculo', max_length=200)
    patente = models.CharField('Identificacion Patente/Codigo', max_length=200)
    #Interno
    token = models.CharField('Token', max_length=25, default=token_ingreso, unique=True)
    fecha = models.DateTimeField('Fecha de registro', default=timezone.now)
    estado = models.CharField('Estado', choices=ESTADO_INGRESO, max_length=1, default='E')
    #Pasajeros
    individuos = models.ManyToManyField(Individuo, related_name='ingresante')
    #Archivos Opcionales
    dut = models.FileField('Permiso Nacional de Circulacion', upload_to='ingresos/', null=True, blank=True)
    plan_vuelo = models.FileField('Plan de Vuelo', upload_to='ingresos/', null=True, blank=True)

#Señales
from .signals import enviar_mail_aprobacion#Al Ingreso de Provincia

#Auditoria
#auditlog.register(Permiso)
auditlog.register(IngresoProvincia)