#Imports de django
from django.db import models
from django.utils import timezone
#Imports extras
from tinymce.models import HTMLField
#Imports del proyecto
from operadores.models import SubComite, Operador
#Imports de la app
from .choices import TIPO_ARCHIVO

# Create your models here.
class Documento(models.Model):
    subcomite = models.ForeignKey(SubComite, on_delete=models.CASCADE, null=True, related_name="documentos")
    nombre = models.CharField('Nombre', max_length=200)
    tipo = models.CharField('Tipo Archivo', max_length=3, choices=TIPO_ARCHIVO, default='WRD')
    autor = models.CharField('Autor', max_length=100)
    publico = models.BooleanField(default=False)
    def __str__(self):
        return self.nombre + '-' + self.tipo + '-' + self.autor
    def ultima_version(self):
        if self.versiones.all():
            return [v for v in self.versiones.all()][-1]
        else:
            return None

class Protocolo(models.Model):
    actividad = models.CharField('Actividad', max_length=200)
    archivo = models.FileField('Archivo', upload_to='protocolos/')
    fecha = models.DateTimeField('Fecha Subido', default=timezone.now)
    activo = models.BooleanField(default=True)

class Version(models.Model):
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='versiones')
    archivo = models.FileField('Archivo', upload_to='documentos/', null=True, blank=True)
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name='versiones')
    cambios = HTMLField()
    fecha = models.DateTimeField('Fecha Subido', default=timezone.now)
    def __str__(self):
        return str(self.fecha)