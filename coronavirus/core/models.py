#Imports de python

#Imports django
from django.db import models
#Extra modules import
from tinymce.models import HTMLField
from auditlog.registry import auditlog
#Imports del proyecto
from coronavirus.settings import DEBUG
#Imports de la app
from .choices import TIPO_LOG

#Modelos
# Create your models here.
class Faq(models.Model):
    orden = models.IntegerField()
    pregunta = models.CharField('Titulo', max_length=200)
    respuesta = HTMLField()
    class Meta:
        ordering = ['orden']
    def __str__(self):
        return self.pregunta
    def as_dict(self):
        return {
            "id": int(self.id),
            "orden": int(self.orden),
            "pregunta": self.pregunta,
            "respuesta": self.respuesta,
        }

class Consulta(models.Model):
    autor = models.CharField('Nombre y Apellido', max_length=100)
    email = models.EmailField('Correo Electronico Personal')
    telefono = models.CharField('Telefono', max_length=50, blank=True, null=True)
    asunto = models.CharField('Asunto', max_length=100)
    descripcion = HTMLField()
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    valida = models.BooleanField('Email Validado', default=False)
    def __str__(self):
        return self.autor + ": " + self.asunto + '(' + str(self.fecha_consulta.date()) + ')'

# Create your models here.
    # Matricula del Vehiculo
    # Tipo de Vehiculo (Definir listado finito y abarcativo de tipos de vehiculos)
    # En caso de ser un viaje comercial: EMPRESA
    # Certificado de Desinfeccion (Bool)
    # Origen
    # Destino
    # De ser posible datos del Alojamiento
    # Plan de Ruta (En caso de no ser un viaje directo)
    # Numero de Pasajeros
    # Datos de CADA UNO de los pasajeros  (Aqui se definira en el COE si solo los pasajeros de riesgo, los aledaños o TODOS) 
    # Nacionalidad
    # Documento de Identidad/Pasaporte(En caso de Extranjeros)
    # Apellidos
    # Nombres
    # Listado de paises visitados (Con fecha de egreso de cada pais)
    # Numero Telefonico ACTIVO o Correo Electronico
    # Observaciones particulares del Pasajero
    # Fecha y Hora del Registro
    # Inspector a cargo del registro

#Auditoria
auditlog.register(Faq)
#Señales
if not DEBUG:
    from core.signals import enviar_mail_new_user