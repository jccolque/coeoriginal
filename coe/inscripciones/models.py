#Imports de Django
from django.db import models
from django.utils import timezone
#Imports extras
from tinymce.models import HTMLField
#Imports del proyecto
from informacion.models import Individuo
#Imports de la app
from .choices import TIPO_INSCRIPTO, GRUPO_SANGUINEO, TIPO_PROFESIONAL, TIPO_DISPOSITIVO

# Create your models here.
class Area(models.Model):
    nombre = models.CharField('Nombres', max_length=250)
    orden = models.IntegerField('Prioridad')
    def __str__(self):
        return self.nombre

class Tarea(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="tareas")
    nombre = models.CharField('Nombres', max_length=250)
    orden = models.IntegerField('Prioridad')
    def __str__(self):
        return self.nombre

class Inscripto(models.Model):
    tipo_inscripto = models.CharField(choices=TIPO_INSCRIPTO, max_length=2, default='PS')
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, null=True, blank=True, related_name="voluntarios")
    profesion = models.IntegerField('Profesion', choices=TIPO_PROFESIONAL, null=True, blank=True)
    matricula = models.CharField(max_length=20, null=True, blank=True)
    oficio = models.CharField("Profesion u Oficio", max_length=100, null=True, blank=True)
    archivo_dni = models.FileField('Foto DNI', upload_to='inscripciones/documentos/')
    archivo_titulo = models.FileField('Foto Titulo', upload_to='inscripciones/titulo/', null=True, blank=True)
    info_extra = HTMLField(null=True, blank=True)
    #grupo_sanguineo = models.IntegerField('Grupo Sanguineo', choices=GRUPO_SANGUINEO, null=True, blank=True)
    #dona_sangre = models.BooleanField(default=False, null=True, blank=True)
    tiene_internet = models.BooleanField(default=False, null=True, blank=True)
    fecha = models.DateTimeField('Fecha Inscripcion', default=timezone.now)
    valido = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True)
    def __str__(self):
        try:
            return self.individuo.apellidos + ', ' + self.individuo.nombres
        except:
            return "Sin Individuo"
    def as_dict(self):
        return {
            'id': self.id,
            'individuo': self.individuo.id,
            'profesion': self.get_profesion_display(),
            'matrícula': self.matricula,
            'archivo_dni': str(self.archivo_dni),
            'archivo_título': str(self.archivo_titulo),
            'info_extra': self.info_extra,
            'fecha': str(self.fecha),
            'valido': self.valido,
            'disponible': self.disponible,
        }

class TareaElegida(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name="elecciones")
    inscripto = models.ForeignKey(Inscripto, on_delete=models.CASCADE, related_name="elecciones")

class Dispositivo(models.Model):
    inscripto = models.ForeignKey(Inscripto, on_delete=models.CASCADE, related_name="dispositivos")
    tipo = models.CharField('Tipo Dispositivo', choices=TIPO_DISPOSITIVO, max_length=2)