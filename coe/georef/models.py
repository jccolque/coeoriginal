#Realizamos imports de Django
from django.db import models
#Imports de paquetes extras
from auditlog.registry import auditlog
from tinymce.models import HTMLField
#Imports de la app
from .choices import TIPO_UBICACION

# Create your models here.
class Nacionalidad(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    riesgo = models.BooleanField(default=True)
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

class Provincia(models.Model):
    nacion = models.ForeignKey(Nacionalidad, on_delete=models.CASCADE, related_name="provincias")
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    class Meta:
        ordering = ['nombre', ]
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
        ordering = ['nombre', ]
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
    codigo_postal = models.CharField('Codigo Postal', max_length=100, blank=True, null=True)
    class Meta:
        ordering = ['nombre', ]
        verbose_name_plural = 'Localidades'
        unique_together = ('departamento', 'nombre')
    def __str__(self):
        return self.nombre + ' (' + str(self.departamento) + ')'
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
        ordering = ['nombre', ]
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

#Particularidades:
class Ubicacion(models.Model):
    tipo = models.CharField('Tipo de Ubicacion', max_length=2, choices=TIPO_UBICACION,  default='SU')
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, related_name="ubicaciones")
    barrio = models.ForeignKey(Barrio, on_delete=models.SET_NULL, related_name="ubicaciones", null=True, blank=True)
    nombre = models.CharField('Nombre', max_length=100)
    capacidad_maxima = models.IntegerField('Capacidad Maxima Permitida', default=50)
    capacidad_ocupada = models.IntegerField('Capacidad Ocupada', default=0)
    calle = models.CharField('Calle', max_length=200)
    numero = models.CharField('Numero', max_length=100)
    telefono = models.CharField('Telefono', max_length=50, default='+549388', null=True, blank=True)
    aclaracion = HTMLField(null=True, blank=True)
    latitud = models.DecimalField('latitud', max_digits=12, decimal_places=10, null=True)
    longitud = models.DecimalField('longitud', max_digits=12, decimal_places=10, null=True)
    def __str__(self):
        return self.get_tipo_display() + ':' + self.nombre + ", " + str(self.localidad)
    def as_dict(self):
        return {
            "id": self.id,
            "tipo_id": self.tipo,
            "tipo": self.get_tipo_display(),
            "nombre": self.nombre,
            "localidad_id": self.localidad.id,
            "calle": self.calle,
            "numero": self.numero,
            "aclaracion": self.aclaracion,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "max_individuos": self.max_individuos,
        }
    def capacidad_disponible(self):
        return self.capacidad_maxima - self.capacidad_ocupada
    def aislados_actuales(self):
        actuales = set()
        for domicilio in self.aislados.all().select_related('individuo'):
            if domicilio.individuo not in actuales:#Para no procesar al pedo.
                individuo = domicilio.individuo
                if domicilio == individuo.domicilio_actual:
                    actuales.add(individuo)
        return actuales
#Auditoria
auditlog.register(Nacionalidad)
auditlog.register(Provincia)
auditlog.register(Departamento)
auditlog.register(Localidad)
auditlog.register(Barrio)
