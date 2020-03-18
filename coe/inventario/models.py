#Import standard de Djagno
from django.db import models
from django.utils import timezone
#Import Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from operadores.models import Operador
from tareas.models import Tarea
#Imports de la app
from .choices import TIPO_EVENTO_ITEM

# Create your models here.
class Rubro(models.Model):
    nombre = models.CharField('Nombre', max_length=200)
    class Meta:
        ordering = ['nombre', ]
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
        }

class SubGrupo(models.Model):
    rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, related_name="grupos")
    nombre = models.CharField('Nombre', max_length=200)
    class Meta:
        unique_together = ['rubro', 'nombre']
        ordering = ['rubro', 'nombre', ]
    def __str__(self):
        return str(self.rubro) + ': ' + self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'rubro_id': self.rubro.id,
            'rubro':self.rubro.nombre,
            'nombre': self.nombre,
        }
    def cantidad_disponible(self):
        return sum([i.cantidad_disponible() for i in self.items.all()])
    def cantidad_distribuida(self):
        return sum([i.cantidad_distribuida() for i in self.items.all()])

class Item(models.Model):
    subgrupo = models.ForeignKey(SubGrupo, on_delete=models.CASCADE, related_name="items")
    nombre = models.CharField('Identificacion', max_length=200)
    responsable = models.ForeignKey(Operador, on_delete=models.CASCADE, null=True, blank=True, related_name="responsable_items")
    class Meta:
        unique_together = ['subgrupo', 'nombre']
        ordering = ['subgrupo', 'nombre', ]
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'grupo_id': self.subgrupo.id,
            'grupo': self.subgrupo.nombre,
            'nombre': self.nombre,
            'responsable': str(self.responsable),
            'situacion': self.situacion,
        }
    def cantidad_disponible(self):
        eventos = self.eventos.all()
        ingresos = sum([e.cantidad for e in eventos.filter(accion='I')])
        retiros = sum([e.cantidad for e in eventos.filter(accion='R')])
        return ingresos - retiros
    def cantidad_distribuida(self):
        return sum([e.cantidad for e in self.eventos.filter(accion='R')])

class EventoItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="eventos")
    accion = models.CharField('Accion', max_length=1 ,choices=TIPO_EVENTO_ITEM, default='I')
    cantidad = models.IntegerField('Cantidad', default=1)
    actuante = models.CharField('Actuante', max_length=200)
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, null=True, blank=True, related_name="recursos")
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="eventos")
    fecha = models.DateTimeField('Fecha del evento', default=timezone.now)
    detalle = HTMLField('Detalle de la accion:')
    devuelto = models.BooleanField(default=False)
    def __str__(self):
        return str(self.item) + ': ' + str(self.fecha) + ' - ' + self.get_accion_display()
    def as_dict(self):
        return {
            'id': self.id,
            'item_id': self.item.id,
            'item': self.nombre,
            'actuante': self.actuante,
            'tarea': str(self.tarea),
            'operador_id': self.operador.id,
            'operador': str(self.operador),
            'accion': self.get_accion_display(),
            'fecha': str(self.fecha),
            'detalle': self.detalle,
        }
#Auditoria
auditlog.register(Item)
auditlog.register(EventoItem)