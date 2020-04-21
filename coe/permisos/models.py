#Imports de python
import qrcode
#Imports de django
from django.db import models
from django.utils import timezone
#Imports de paquetes extras
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import STATIC_ROOT, MEDIA_ROOT
from georef.models import Provincia, Localidad
from informacion.models import Individuo
#Imports de app
from .choices import TIPO_PERMISO
from .choices import TIPO_INGRESO, ESTADO_INGRESO
from .tokens import generar_token

# Create your models here.
class Permiso(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="permisos")
    tipo = models.CharField('Tipo Permiso', choices=TIPO_PERMISO, max_length=1, default='C')
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="permisos")
    begda = models.DateTimeField('Inicio Permiso', default=timezone.now)
    endda = models.DateTimeField('Fin Permiso', default=timezone.now)
    controlador = models.BooleanField(default=False)
    aclaracion = HTMLField(null=True, blank=True)
    #Interno
    #token = models.CharField('Token', max_length=35, default=generar_token, unique=True)
    #fecha = models.DateTimeField('Fecha de registro', default=timezone.now)
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
    origen = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="ingresos")
    destino = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="ingresos")
    #Vehiculo
    marca = models.CharField('Marca del Vehiculo', max_length=200)
    modelo = models.CharField('Modelo del Vehiculo', max_length=200)
    patente = models.CharField('Identificacion Patente/Codigo', max_length=200)
    #Interno
    token = models.CharField('Token', max_length=35, default=generar_token, unique=True)
    fecha = models.DateTimeField('Fecha de registro', default=timezone.now)
    estado = models.CharField('Estado', choices=ESTADO_INGRESO, max_length=1, default='C')
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    #Aclaraciones
    aclaracion = HTMLField(null=True)
    #Pasajeros
    individuos = models.ManyToManyField(Individuo, related_name='ingresante')
    #Archivos
    permiso_nacional = models.FileField('Permiso Nacional de Circulacion', upload_to='ingresos/')
    dut = models.FileField('Permiso Nacional de Circulacion', upload_to='ingresos/', null=True, blank=True)
    plan_vuelo = models.FileField('Plan de Vuelo', upload_to='ingresos/', null=True, blank=True)
    def get_qr(self):
        if self.qrpath:
            return self.qrpath
        else:
            path = MEDIA_ROOT + '/permisos/qrcode-'+str(self.id)+'.png'
            img = qrcode.make(self.token)
            img.save(path)
            relative_path = 'archivos/permisos/qrcode-'+ str(self.id)+'.png'
            self.qrpath = relative_path
            self.save()
            return self.qrpath
    def generar_pdf(self):
        pdf = canvas.Canvas("archivos/permisos/"+self.token+".pdf", pagesize=A4)
        pdf.drawString(10,650,"PERMISO DE INGRESO A JUJUY")
        pdf.drawString(10,630,self.get_tipo_display())
        pdf.drawString(10,600,"Fecha de llegada: "+str(self.fecha_llegada)[0:16])
        pdf.drawString(10,585,"Origen del Viaje: "+str(self.origen))
        pdf.drawString(10,570,"Destino del Viaje: "+str(self.destino))
        pdf.drawString(10,555,"Vehiculo: "+self.marca+" "+self.modelo+" "+self.patente)
        #Agregamos lista de pasajeros
        if self.individuos.exists():#Si existe
            pdf.drawString(10,530,"Pasajeros:")
            altura=500
            for individuo in self.individuos.all():
                pdf.drawString(10,altura, str(individuo))
                altura-= 20
        #Cargamos imagenes
        pdf.drawImage(STATIC_ROOT+'/img/logo_pdf.png', 50, 700, height=50*mm, preserveAspectRatio=True)
        pdf.drawImage(self.get_qr(), 400, 700, 50*mm, 50*mm)
        pdf.save()

#Señales

#Auditoria
#auditlog.register(Permiso)
auditlog.register(IngresoProvincia)