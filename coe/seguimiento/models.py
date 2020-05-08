#Import de python
from datetime import timedelta
#Imports Django
from django.db import models
from django.utils import timezone
#Imports Extras
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import LOADDATA
from operadores.models import Operador
from informacion.models import Individuo

# Create your models here.
class Vigia(models.Model):
    operador = models.OneToOneField(Operador, on_delete=models.CASCADE, related_name="vigia")
    controlados = models.ManyToManyField(Individuo, related_name='vigilador')
    def __str__(self):
        return str(self.operador.nombres) + ' ' + str(self.operador.apellidos)
    def alertas_activas(self):
        limite = timezone.now() - timedelta(hours=12)
        return self.controlados.exclude(seguimientos__fecha__gt=limite).count()

if not LOADDATA:
    #Auditoria
    auditlog.register(Vigia)
    #Señales