#Imports de django
from django.db import models
from django.utils import timezone
#Imports Extras
from auditlog.registry import auditlog
#Imports del proyecto
from core.models import Aclaracion
#Imports de la app
from .choices import  TIPO_DENUNCIA, ESTADO_DENUNCIA

# Create your models here.
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

#Auditoria
auditlog.register(DenunciaAnonima)
