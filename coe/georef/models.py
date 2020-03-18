#Realizamos imports de Django
from django.db import models
#Imports de paquetes extras
from auditlog.registry import auditlog
from tinymce.models import HTMLField

# Create your models here.
class Provincia(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    class Meta:
        verbose_name_plural = 'Provincias'
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            "id": self.id,
            "provincia_id": self.id,
            "nombre": self.nombre,
        }

class Departamento(models.Model):#Departamento
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="departamentos")
    nombre = models.CharField('Nombre', max_length=100)
    class Meta:
        verbose_name_plural = 'Departamentos'
        unique_together = ('provincia', 'nombre')
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            "id": self.id,
            "provincia_id": self.provincia.id,
            "departamento_id": self.id,
            "nombre": self.nombre,
        }

class Localidad(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name="localidades")
    nombre = models.CharField('Nombre', max_length=100)
    codigo_postal = models.CharField('Codigo Postal', max_length=50, blank=True, null=True)
    class Meta:
        verbose_name_plural = 'Localidades'
        unique_together = ('departamento', 'nombre')
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            "id": self.id,
            "departamento_id": self.departamento.id,
            "localidad_id": self.id,
            "nombre": self.nombre,
            "codigo_postal": self.codigo_postal,
        }

class Barrio(models.Model):
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="barrios")
    nombre = models.CharField('Nombre', max_length=100)
    class Meta:
        unique_together = ('localidad', 'nombre')
        verbose_name_plural = 'Barrios'
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            "id": self.id,
            "localidad_id": self.localidad.id,
            "barrio_id": self.id,
            "nombre": self.nombre,
        }

class Nacionalidad(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    riesgo = models.BooleanField(default=False)
    contacto = HTMLField(null=True, blank=True)
    class Meta:
        ordering = ['nombre', ]
        verbose_name_plural = 'Nacionalidades'
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "riesgo": self.riesgo,
            "contacto": self.contacto,
        }

#Auditoria
auditlog.register(Provincia)
auditlog.register(Departamento)
auditlog.register(Localidad)
auditlog.register(Barrio)