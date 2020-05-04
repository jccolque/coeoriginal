#Imports de python
import io
import qrcode
#Imports de django
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
#Imports de paquetes extras
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyPDF2 import PdfFileWriter, PdfFileReader
from tinymce.models import HTMLField
from auditlog.registry import auditlog
from multiselectfield import MultiSelectField
#Imports del proyecto
from coe.settings import BASE_DIR, STATIC_ROOT, MEDIA_ROOT, LOADDATA
from georef.models import Provincia, Localidad
from informacion.models import Individuo
from operadores.models import Operador
#Imports de app
from .choices import COLOR_RESTRICCION, GRUPOS_PERMITIDOS
from .choices import TIPO_PERMISO, TIPO_CIRCULACION
from .choices import COMBINACION_DNIxDIA
from .choices import TIPO_INGRESO, ESTADO_INGRESO
from .tokens import token_ingreso

# Create your models here.
class NivelRestriccion(models.Model):
    color = models.CharField('Nivel de Restriccion', choices=COLOR_RESTRICCION, max_length=1, default='B', unique=True)
    inicio_horario = models.SmallIntegerField("Hora de Inicio Actividades/f24")
    cierre_horario = models.SmallIntegerField("Hora de cierre Actividades/f24")
    poblacion_maxima = models.SmallIntegerField('Capacidad Adminitada en %')
    tramites_admitidos = MultiSelectField(choices=TIPO_PERMISO, null=True, blank=True)
    duracion_permiso = models.SmallIntegerField("Duracion de Permisos Digitales", default=1)
    grupos_diarios = MultiSelectField(choices=COMBINACION_DNIxDIA, null=True, blank=True)
    fecha_activacion = models.DateTimeField('Fecha de Activacion', null=True, blank=True)
    activa = models.BooleanField(default=False)

class Permiso(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="permisos")
    tipo = models.CharField('Tipo Permiso', choices=TIPO_PERMISO, max_length=1, default='C')
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="permisos")
    begda = models.DateTimeField('Inicio Permiso', default=timezone.now)
    endda = models.DateTimeField('Fin Permiso', default=timezone.now)
    controlador = models.BooleanField(default=False)
    aclaracion = HTMLField(null=True, blank=True)
    #Interno
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="permisos")
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
    origen = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="ingresos_provincial")
    destino = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="ingresos_provincial")
    #Vehiculo
    marca = models.CharField('Marca del Vehiculo', max_length=200)
    modelo = models.CharField('Modelo del Vehiculo', max_length=200)
    patente = models.CharField('Identificacion Patente/Codigo', max_length=200)
    #Interno
    token = models.CharField('Token', max_length=50, default=token_ingreso, unique=True)
    fecha = models.DateTimeField('Fecha de registro', default=timezone.now)
    estado = models.CharField('Estado', choices=ESTADO_INGRESO, max_length=1, default='C')
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="ingresos_provinciales")
    #Aclaraciones
    aclaracion = HTMLField(null=True)
    #Pasajeros
    individuos = models.ManyToManyField(Individuo, related_name='ingresante')
    #Archivos
    permiso_nacional = models.FileField('Permiso Nacional de Circulacion', upload_to='ingresos/')
    dut = models.FileField('Permiso Nacional de Circulacion', upload_to='ingresos/', null=True, blank=True)
    plan_vuelo = models.FileField('Plan de Vuelo', upload_to='ingresos/', null=True, blank=True)
    def telefono(self):
        try:
            return self.individuos.all()[0].telefono
        except:
            return 'Sin informar'
    def get_qr(self):
        if self.qrpath:
            return self.qrpath
        else:
            path = MEDIA_ROOT + '/permisos/qrcode-'+str(self.id)+'.png'
            img = qrcode.make(self.token)#TIENE QUE SER URL A: redirect> 'permisos:ver_ingreso_aprobado' token=ingreso.token
            img.save(path)
            relative_path = 'archivos/permisos/qrcode-'+ str(self.id)+'.png'
            self.qrpath = relative_path
            self.save()
            return self.qrpath
    def generar_pdf(self):
        packet = io.BytesIO()
        # Se crear un nuevo pdf utilizando ReportLab        
        pdf = canvas.Canvas(packet, pagesize=A4)
        #escribimos textos del pdf
        #Fechamos
        pdf.setFont('Times-Roman', 9)
        pdf.drawString(475, 680, str(timezone.now())[0:16])
        #Armamos documento de permiso de ingreso a Jujuy
        pdf.setFont('Times-Roman', 18)
        pdf.drawString(20, 650, "PERMISO DE INGRESO A JUJUY")
        pdf.setFont('Times-Roman', 12)
        pdf.drawString(30, 630, self.get_tipo_display())
        pdf.drawString(30, 600, "Fecha de llegada: "+str(self.fecha_llegada)[0:16])
        pdf.drawString(30, 585, "Origen del Viaje: "+str(self.origen))
        pdf.drawString(30, 570, "Destino del Viaje: "+str(self.destino))
        pdf.drawString(30, 555, "Vehiculo: "+self.marca+" "+self.modelo+" "+self.patente)
        #Agregamos una linea
        pdf.line(200, 520, 400, 520)
        #Agregamos lista de pasajeros
        if self.individuos.exists():#Si existe
            pdf.drawString(30,530, "Pasajeros:")
            altura=500
            for individuo in self.individuos.all():
                pdf.drawString(30, altura, str(individuo))
                altura-= 20
        pdf.drawImage(self.get_qr(), 420, 520, 50*mm, 50*mm)
        pdf.save()
        #Se comienza el procedimiento para mergear pdfs
        packet.seek(0)
        nuevo_pdf = PdfFileReader(packet)
        # Leemos el pdf base
        existe_pdf = PdfFileReader(STATIC_ROOT+'/archivos/plantilla_nota.pdf', "rb")
        salida = PdfFileWriter()
        # Se agregan los datos de la persona que será dada de alta, al pdf ya existente
        pagina = existe_pdf.getPage(0)
        pagina.mergePage(nuevo_pdf.getPage(0))
        salida.addPage(pagina)
        #Finalmente se escribe la salida, en un archivo real
        outputStream = open(MEDIA_ROOT+'/permisos/'+self.token+".pdf", "wb")
        salida.write(outputStream)
        outputStream.close()

class Emails_Ingreso(models.Model):
    ingreso = models.ForeignKey(IngresoProvincia, on_delete=models.CASCADE, related_name="emails")
    fecha = models.DateTimeField('Fecha de Envio', default=timezone.now)
    asunto = models.CharField('Asunto', max_length=100)
    cuerpo = models.CharField('Cuerpo', max_length=1000)
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="ingreso_emailsenviados")

class CirculacionTemporal(models.Model):#Transportes de Carga
    tipo = models.CharField('Tipo Circulacion', choices=TIPO_CIRCULACION, max_length=2, default='CC')
    email_contacto = models.EmailField('Correo Electronico de Contacto')
    chofer = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="transportista", null=True, blank=True)
    acompañante = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="acompañante", null=True, blank=True)
    actividad = HTMLField(null=True)
    origen = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="ingresos_transporte")
    destino = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="ingresos_transporte")
    #Vehiculo
    marca = models.CharField('Marca del Vehiculo', max_length=200)
    modelo = models.CharField('Modelo del Vehiculo', max_length=200)
    patente = models.CharField('Identificacion Patente', max_length=200)
    #Archivos
    permiso_nacional = models.FileField('Permiso Nacional de Circulacion', upload_to='ingresos/', null=True, blank=True)
    licencia_conducir = models.FileField('Licencia de Conducir', upload_to='ingresos/', null=True, blank=True)
    #Interno
    token = models.CharField('Token', max_length=50, default=token_ingreso, unique=True)
    fecha = models.DateTimeField('Fecha de registro', default=timezone.now)
    estado = models.CharField('Estado', choices=ESTADO_INGRESO, max_length=1, default='C')
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    def listo(self):
        #Chequeamos que haya cargado permiso y licencia
        lista = hasattr(self, 'permiso_nacional') and hasattr(self, 'licencia_conducir')
        if lista:#Chequeamos que haya cargado Chofer
            lista = hasattr(self, 'chofer')
        if lista:#Chequeamos que chofer tenga App
            lista = hasattr(self.chofer, 'appdata')
        return lista
    def get_qr(self):
        if self.qrpath:
            return self.qrpath
        else:
            path = MEDIA_ROOT + '/circulacion/qrcode-'+str(self.id)+'.png'
            img = qrcode.make(self.token)#TIENE QUE SER URL A: redirect> 'permisos:ver_ingreso_aprobado' token=ingreso.token
            img.save(path)
            relative_path = 'archivos/circulacion/qrcode-'+ str(self.id)+'.png'
            self.qrpath = relative_path
            self.save()
            return self.qrpath
    def generar_pdf(self):  ##### AGREGAR QR
        packet = io.BytesIO()
        # Se crear un nuevo pdf utilizando ReportLab
        pdf = canvas.Canvas(packet, pagesize=A4)
        #escribimos textos del pdf
        #Fechamos
        pdf.setFont('Times-Roman', 9)
        pdf.drawString(475, 680, str(timezone.now())[0:16])
        #Armamos documento
        pdf.setFont('Times-Roman', 18)
        pdf.drawString(30, 650, "PERMISO DE CIRCULACION TEMPORAL")
        pdf.setFont('Times-Roman', 12)
        pdf.drawString(30, 630, "Tipo: " + self.get_tipo_display())
        pdf.drawString(30, 585, "Origen del Viaje: "+str(self.origen))
        pdf.drawString(30, 570, "Destino del Viaje: "+str(self.destino))
        pdf.drawString(30, 555, "Vehiculo: " + self.marca + " " + self.modelo + " - Patente" + self.patente)
        pdf.drawString(30, 540, "Actividad: " + strip_tags(self.actividad))
        #Datos del Chofer
        pdf.line(200, 520, 400, 520)
        pdf.drawString(30, 500, "Chofer: "+str(self.chofer))
        pdf.drawString(45, 485, "Telefono: "+ self.chofer.telefono)
        if self.acompañante:
            pdf.drawString(30, 460, "Chofer: "+str(self.acompañante))
            pdf.drawString(45, 445, "Telefono: "+ self.acompañante.telefono)
        #Agregamos licencia de conducir
        pdf.line(200, 420, 400, 420)
        pdf.drawString(30, 400, "Licencia de Conducir: ")
        pdf.drawImage(BASE_DIR+self.licencia_conducir.url, 50, 230, 75*mm, 50*mm)
        #Agregamos Codigo QR
        pdf.drawImage(self.get_qr(), 420, 520, 50*mm, 50*mm)
        #Grabamos el PDF
        pdf.save()
        packet.seek(0)
        nuevo_pdf = PdfFileReader(packet)
        # Leemos el pdf base
        existe_pdf = PdfFileReader(STATIC_ROOT+'/archivos/plantilla_nota.pdf', "rb")
        salida = PdfFileWriter()
        # Se agregan los datos de la persona que será dada de alta, al pdf ya existente
        pagina = existe_pdf.getPage(0)
        pagina.mergePage(nuevo_pdf.getPage(0))
        salida.addPage(pagina)
        #Finalmente se escribe la salida, en un archivo real
        outputStream = open(MEDIA_ROOT+'/circulacion/'+self.token+".pdf", "wb")
        salida.write(outputStream)
        outputStream.close()  

class Emails_Circulacion(models.Model):
    circulacion = models.ForeignKey(CirculacionTemporal, on_delete=models.CASCADE, related_name="emails")
    fecha = models.DateTimeField('Fecha de Envio', default=timezone.now)
    asunto = models.CharField('Asunto', max_length=100)
    cuerpo = models.CharField('Cuerpo', max_length=1000)
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="circulacion_emailsenviados")

if not LOADDATA:
    #señales
    from .signals import activar_restriccion

    #Auditoria
    auditlog.register(Permiso)
    auditlog.register(NivelRestriccion)
    auditlog.register(IngresoProvincia)