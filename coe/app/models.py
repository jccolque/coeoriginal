#Imports de django
from django.db import models
from django.utils import timezone
#Imports Extras
from auditlog.registry import auditlog
from fcm_django.models import FCMDevice
#Imports del proyecto
from informacion.models import Individuo
#Imports de la app
from .choices import TIPO_TRIAJE
from .choices import TIPO_ACCION_NOTIFICACION

# Create your models here.
class AppData(models.Model):
    individuo = models.OneToOneField(Individuo, on_delete=models.CASCADE, related_name="appdata")
    telefono = models.CharField('Telefono', max_length=50, default='+549388')
    email = models.EmailField('Correo Electronico', null=True, blank=True)#Enviar mails
    estado = models.CharField('Estado', choices=TIPO_TRIAJE, max_length=1, default='V')
    device = models.OneToOneField(FCMDevice, on_delete=models.SET_NULL, null=True, blank=True, related_name="appdata")
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)
    #GeoTracking
    intervalo = models.IntegerField("Intervalo entre Trackings",default=10)#Minutos
    distancia_alerta = models.IntegerField("Distancia de Alerta", default=50)#Mts
    distancia_critica = models.IntegerField("Distancia Critica", default=100)#Mts
    def __str__(self):
        return str(self.individuo) + self.get_estado_display()

class AppNotificacion(models.Model):
    appdata = models.OneToOneField(AppData, on_delete=models.CASCADE, related_name="notificacion")
    titulo = models.CharField('titulo', max_length=100, default='', blank=False)
    mensaje = models.CharField('mensaje', max_length=200, default='', blank=False)
    accion = models.CharField('accion', choices=TIPO_ACCION_NOTIFICACION, max_length=2, default='SM')
    fecha = models.DateTimeField('Fecha del Registro', default=timezone.now)

#Señales
from .signals import enviar_push

