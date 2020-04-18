#Imports de django
from django.db import models
from django.utils import timezone
#Imports de paquetes extras
from tinymce.models import HTMLField
#Imports del proyecto
from georef.models import Localidad
from informacion.models import Individuo
#Imports de app
from .choices import TIPO_PERMISO

# Create your models here.
class Permiso(models.Model):
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, related_name="permisos")
    tipo = models.CharField('Tipo Permiso', choices=TIPO_PERMISO, max_length=1, default='C')
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="permisos")
    begda = models.DateTimeField('Inicio Permiso', default=timezone.now)
    endda = models.DateTimeField('Fin Permiso', default=timezone.now)
    controlador = models.BooleanField(default=False)
    aclaracion = HTMLField(null=True, blank=True)
    def __str__(self):
        return self.get_tipo_display() + str(self.begda)[0:16]
    def estado(self):
        if self.endda > timezone.now():
            return "Activo"
        else:
            return "Vencido"