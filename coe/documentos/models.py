#Imports de django
from django.db import models
from django.utils import timezone
#Imports del proyecto
from operadores.models import SubComite, Operador
#Imports de la app
from .choices import TIPO_ARCHIVO

# Create your models here.
class Documento(models.Model):
    subcomite = models.ForeignKey(SubComite, on_delete=models.CASCADE, null=True, related_name="documentos")
    nombre = models.CharField('Nombre', max_length=200)
    tipo = models.CharField('Tipo Archivo', max_length=3, choices=TIPO_ARCHIVO)
    autor = models.CharField('Autor', max_length=100)

class Version(models.Model):
    archivo = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='versiones')
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name='versiones')
    fecha = models.DateTimeField('Inicio', default=timezone.now)