#Import standard de Djagno
from django.db import models
from django.utils import timezone
#Import Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from operadores.models import SubComite, Operador
#Imports de la app
from .choices import TIPO_PRIORIDAD, TIPO_EVENTO_TAREA

# Create your models here.
class Tarea(models.Model):
    subcomite = models.ForeignKey(SubComite, on_delete=models.CASCADE, null=True, related_name="tareas")
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = HTMLField()
    prioridad = models.IntegerField(choices=TIPO_PRIORIDAD, default=0)
    begda = models.DateTimeField('Inicio', default=timezone.now)
    endda = models.DateTimeField('Limite', default=timezone.now)
    class Meta:
        ordering = ('-prioridad', 'endda')
    def __str__(self):
        return self.nombre + ': ' + self.get_prioridad_display()
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'prioridad': self.get_prioridad_display(),
            'begda': str(self.begda),
            'endda': str(self.endda),
        }
    def get_last_event(self):
        return self.eventos.order_by('fecha').last()
    def hrs_restantes(self):
        ahora = timezone.now()
        restante = self.endda - ahora
        return int(restante.total_seconds() / 3600)
    def recursos_actuales(self):
        return self.recursos.filter(accion='R', devuelto=False)

class Responsable(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, null=True, related_name="responsables")
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="responsables")
    fecha_asignacion = models.DateTimeField('Fecha de Asignacion', default=timezone.now)
    obligaciones = HTMLField()
    def __str__(self):
        return 'Tarea'
    def as_dict(self):
        return {
            'id': self.id,
            'tarea_id': self.tarea.id,
            'tarea': str(self.tarea),
            'operador_id': self.operador.id,
            'operador': str(self.operador),
            'fecha_asignacion': str(self.fecha_asignacion),
            'obligaciones': self.obligaciones,
        }

class EventoTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, null=True, related_name="eventos")
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE, null=True, blank=True, related_name="eventos")
    accion = models.CharField(max_length=1, choices=TIPO_EVENTO_TAREA, default='I')
    fecha = models.DateTimeField('Fecha del evento', default=timezone.now)
    detalle = HTMLField(null=True, blank=True)
    def __str__(self):
        return self.get_accion_display() + ': ' + str(self.fecha)
    def as_dict(self):
        return {
            'id': self.id,
            'tarea_id': self.tarea.id,
            'tarea': str(self.tarea),
            'responsable': str(self.responsable),
            'accion': self.get_accion_display(),
            'fecha': str(self.fecha),
            'detalle': self.detalle,
        }

#Auditoria
auditlog.register(Tarea)
auditlog.register(Responsable)
auditlog.register(EventoTarea)