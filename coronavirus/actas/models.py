#Import standard de Djagno
from django.db import models
from django.utils import timezone
#Import Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from operadores.models import Operador
#Imports de la app
from .choices import TIPO_ACTA, TIPO_EVENTO

# Create your models here.
class Acta(models.Model):
    nombre = models.CharField('Nombre', max_length=200)
    cuerpo = HTMLField()
    tipo = models.IntegerField(choices=TIPO_ACTA, default=5)
    fecha = models.DateTimeField('Fecha del Acta', default=timezone.now)
    publica = models.BooleanField('Publicable', default=False)

class Participes(models.Model):
    acta = models.ForeignKey(Acta, on_delete=models.CASCADE, null=True, blank=True, related_name="participes")
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, null=True, blank=True, related_name="participes")

class EventoParticipe(models.Model):
    participe = models.ForeignKey(Participes, on_delete=models.CASCADE, null=True, blank=True, related_name="eventos")
    tipo = models.IntegerField(choices=TIPO_EVENTO, default=1)
    fecha = models.DateTimeField('Fecha', default=timezone.now)

#Auditoria
auditlog.register(Acta)
auditlog.register(Participes)
auditlog.register(EventoParticipe)