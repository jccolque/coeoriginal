#Import standard de Djagno
from django.db import models
from django.utils import timezone
#Import Extras
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from operadores.models import Operador
#Imports de la app
from .choices import TIPO_ACTA

# Create your models here.
class Acta(models.Model):
    nombre = models.CharField('Nombre', max_length=200)
    cuerpo = HTMLField()
    tipo = models.IntegerField(choices=TIPO_ACTA, default=5)
    fecha = models.DateTimeField('Fecha del Acta', default=timezone.now)
    publica = models.BooleanField('Publicable', default=False)
    def __str__(self):
        return self.nombre + ': ' + str(self.fecha)
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cuerpo': self.cuerpo,
            'tipo': self.tipo,
            'fecha': self.fecha,
            'publica': self.publica,
        }


class Participes(models.Model):
    acta = models.ForeignKey(Acta, on_delete=models.CASCADE, related_name="participes")
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="participes")
    def __str__(self):
        return str(self.operador)
    def as_dict(self):
        return {
            'id': self.id,
            'acta_id': self.acta.id,
            'operador': self.operador.id,
        }

#Auditoria
auditlog.register(Acta)
auditlog.register(Participes)