#Import standard de Djagno
from django.db import models
from django.utils import timezone
#Import Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from operadores.models import Operador
#Imports de la app
from .choices import TIPO_EVENTO_ITEM

# Create your models here.
class Item(models.Model):
    nombre = models.CharField('Nombre', max_length=200)
    cantidad = models.IntegerField('Cantidad', default=1)
    proveedor = models.ForeignKey(Operador, on_delete=models.CASCADE, null=True, blank=True, related_name="proveedor_items")
    responsable = models.ForeignKey(Operador, on_delete=models.CASCADE, null=True, blank=True, related_name="responsable_items")
    situacion = HTMLField()
    def __str__(self):
        return self.nombre + ': ' + str(self.cantidad)
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'proveedor': self.proveedor,
            'responsable': str(self.responsable),
            'situacion': self.situacion,
        }

class EventoItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="eventos")
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="eventos")
    accion = models.IntegerField(choices=TIPO_EVENTO_ITEM, default='1')
    fecha = models.DateTimeField('Fecha del evento', default=timezone.now)
    detalle = HTMLField()
    def __str__(self):
        return str(self.item) + ': ' + str(self.fecha) + ' - ' + self.get_accion_display()
    def as_dict(self):
        return {
            'id': self.id,
            'item_id': self.item.id,
            'item': str(self.nombre),
            'operador_id': self.operador.id,
            'operador': str(self.operador),
            'accion': self.get_accion_display(),
            'fecha': str(self.fecha),
            'detalle': self.detalle,
        }
#Auditoria
auditlog.register(Item)
auditlog.register(EventoItem)