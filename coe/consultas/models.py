#Import Python
from datetime import timedelta
#Imports de Django
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
#Imports Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from core.models import Faq, Aclaracion
from coe.settings import LOADDATA
from informacion.models import Individuo
from operadores.models import Operador
#Imports de la app
from .choices import TIPO_LLAMADA, TIPO_TELEFONISTA
from .choices import  TIPO_DENUNCIA, ESTADO_DENUNCIA

# Create your models here.
class Consulta(models.Model):
    num_doc = models.CharField('Numero de Documento/Pasaporte', 
        max_length=50,
        validators=[RegexValidator('^[A-Z_\d]*$', 'Solo Mayusculas.')],
    )
    autor = models.CharField('Nombre Completo', max_length=100)
    email = models.EmailField('Email', blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=100, blank=True, null=True)
    asunto = models.CharField('Asunto', max_length=100)
    descripcion = HTMLField()
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    valida = models.BooleanField('Email Validado', default=False)
    respondida = models.BooleanField('Respondida', default=False)
    class Meta:
        ordering = ['fecha_consulta', ]
    def __str__(self):
        return self.autor + ": " + self.asunto + '(' + str(self.fecha_consulta.date()) + ')'

class DenunciaAnonima(models.Model):
    tipo = models.CharField('Tipo Denuncia', max_length=2, choices=TIPO_DENUNCIA, default='SC')
    descripcion = models.TextField('Descripcion')
    imagen = models.FileField('Imagen', upload_to='denuncias/')
    latitud = models.DecimalField('latitud', max_digits=12, decimal_places=10)
    longitud = models.DecimalField('longitud', max_digits=12, decimal_places=10)
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    estado = models.CharField('Tipo Denuncia', max_length=2, choices=ESTADO_DENUNCIA, default='IN')
    aclaraciones = models.ManyToManyField(Aclaracion)
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.descripcion

class Telefonista(models.Model):
    tipo = models.CharField('Tipo Telefonista', choices=TIPO_TELEFONISTA, max_length=2, default='MX')
    operador = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name="telefonista")
    max_pendientes = models.SmallIntegerField('Cantidad Maxima de Pendientes', default=100)
    consultas = models.ManyToManyField(Consulta, related_name='telefonistas')
    denuncias = models.ManyToManyField(DenunciaAnonima, related_name='telefonistas')
    def __str__(self):
        return str(self.operador.nombres) + ' ' + str(self.operador.apellidos)
    def cant_pendientes(self):
        conteo = sum([1 for c in self.consultas.all()])
        conteo += sum([1 for d in self.denuncias.all()])
        return conteo
    def atenciones_24hrs(self):
        limite = timezone.now() - timedelta(hours=24)
        conteo = sum([1 for r in self.respuestas.all() if r.fecha >= limite])
        conteo += sum([1 for l in self.llamadas.all() if l.fecha >= limite])
        conteo += sum([1 for d in self.operador.aclaraciones.all() if d.fecha >= limite])
        return conteo
    def atenciones_7dias(self):
        limite = timezone.now() - timedelta(hours=24 * 7)
        conteo = sum([1 for r in self.respuestas.all() if r.fecha >= limite])
        conteo += sum([1 for l in self.llamadas.all() if l.fecha >= limite])
        conteo += sum([1 for d in self.operador.aclaraciones.all() if d.fecha >= limite])
        return conteo
    def total(self):
        conteo = sum([1 for r in self.respuestas.all()])
        conteo += sum([1 for l in self.llamadas.all()])
        conteo += sum([1 for d in self.operador.aclaraciones.all()])
        return conteo

class Respuesta(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name="respuestas")
    telefonista = models.ForeignKey(Telefonista, on_delete=models.SET_NULL, blank=True, null=True, related_name="respuestas")
    respuesta = HTMLField()
    fecha = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.consulta) + ": " + self.respuesta

class Llamada(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, blank=True, null=True, related_name="llamadas")
    tipo = models.CharField('Asunto', choices=TIPO_LLAMADA, max_length=2)
    frecuente = models.ForeignKey(Faq, on_delete=models.SET_NULL, blank=True, null=True, related_name="llamadas")
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
    auditlog.register(DenunciaAnonima)