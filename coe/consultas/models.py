#Import Python
from datetime import timedelta
#Imports de Django
from django.db import models
from django.utils import timezone
#Imports Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import LOADDATA
from informacion.models import Individuo
from operadores.models import Operador
#from denuncias.models import DenunciaAnonima
#Imports de la app
from .choices import TIPO_LLAMADA, TIPO_TELEFONISTA


# Create your models here.
class Consulta(models.Model):
    autor = models.CharField('Nombre y Apellido', max_length=100)
    email = models.EmailField('Correo Electronico', blank=True, null=True)
    telefono = models.CharField('Telefono', max_length=100, blank=True, null=True)
    asunto = models.CharField('Asunto', max_length=100)
    descripcion = HTMLField()
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    valida = models.BooleanField('Email Validado', default=False)
    respondida = models.BooleanField('Respondida', default=False)
    class Meta:
        ordering = ['fecha_consulta', ]
    def __str__(self):
        return self.autor + ": " + self.asunto + '(' + str(self.fecha_consulta.date()) + ')'

class Telefonista(models.Model):
    tipo = models.CharField('Tipo Telefonista', choices=TIPO_TELEFONISTA, max_length=2, default='MX')
    operador = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name="telefonista")
    max_pendientes = models.SmallIntegerField('Cantidad Maxima de Pendientes', default=100)
    consultas = models.ManyToManyField(Consulta, related_name='telefonista')
    #denuncias = models.ManyToManyField(DenunciaAnonima, related_name='telefonista')
    def __str__(self):
        return str(self.operador.nombres) + ' ' + str(self.operador.apellidos)
    def atenciones_24hrs(self):
        limite = timezone.now() - timedelta(hours=24)
        conteo = Respuesta.objects.filter(telefonista=self, fecha__gt=limite).count()
        conteo += Llamada.objects.filter(telefonista=self, fecha__gt=limite).count()
        return conteo
    def atenciones_7dias(self):
        limite = timezone.now() - timedelta(hours=24 * 7)
        conteo = Respuesta.objects.filter(telefonista=self, fecha__gt=limite).count()
        conteo += Llamada.objects.filter(telefonista=self, fecha__gt=limite).count()
        return conteo
    def total(self):
        conteo = Respuesta.objects.filter(telefonista=self).count()
        conteo += Llamada.objects.filter(telefonista=self).count()
        return conteo

class Respuesta(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name="respuestas")
    telefonista = models.ForeignKey(Telefonista, on_delete=models.SET_NULL, blank=True, null=True, related_name="respuestas")
    respuesta = HTMLField()
    fecha = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.consulta) + ": " + self.respuesta

class Llamada(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="consultas")
    tipo = models.CharField('Asunto', choices=TIPO_LLAMADA, max_length=2)
    desarrollo = HTMLField()
    fecha = models.DateTimeField(auto_now_add=True)
    resuelta = models.BooleanField('Respondida', default=True)
    telefonista = models.ForeignKey(Telefonista, on_delete=models.SET_NULL, blank=True, null=True, related_name="llamadas")

if not LOADDATA:
    #Auditoria
    auditlog.register(Telefonista)
    auditlog.register(Consulta)
    auditlog.register(Respuesta)
    auditlog.register(Llamada)
