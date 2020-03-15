#Import standard de Djagno
from django.db import models
from django.utils import timezone
#Import Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from operadores.models import Operador
#Imports de la app
from .choices import TIPO_PRIORIDAD, TIPO_EVENTO_TAREA

# Create your models here.
class Tarea(models.Model):
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = HTMLField()
    prioridad = models.IntegerField(choices=TIPO_PRIORIDAD, default=5)
    begda = models.DateTimeField('Inicio', default=timezone.now)
    endda = models.DateTimeField('Limite', default=timezone.now)

class Responsable(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, null=True, related_name="responsables")
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, null=True, blank=True, related_name="responsables")
    fecha_asignacion = models.DateTimeField('Fecha de Asignacion', default=timezone.now)
    obligaciones = HTMLField()

class EventoTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, null=True, related_name="eventos")
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE, null=True, blank=True, related_name="eventos")
    accion = models.IntegerField(choices=TIPO_EVENTO_TAREA, default='1')
    fecha = models.DateTimeField('Fecha del evento', default=timezone.now)
    detalle = HTMLField()

#Auditoria
auditlog.register(Tarea)
auditlog.register(Responsable)
auditlog.register(EventoTarea)