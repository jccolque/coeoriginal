#Imports de Django
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
#Imports extras
from tinymce.models import HTMLField
#Imports del proyecto
from core.choices import TIPO_DOCUMENTOS
#Imports de la app
from .choices import TIPO_PROFESIONAL

# Create your models here.
class Inscripto(models.Model):
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.CharField('Numero de Documento/Pasaporte', 
        max_length=20,
        validators=[RegexValidator('^[A-Z_\d]*$', 'Solo Mayusculas.')],
        unique=True,
    )
    apellidos = models.CharField('Apellidos', max_length=50)
    nombres = models.CharField('Nombres', max_length=50)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    profesion = models.IntegerField('Profesion', choices=TIPO_PROFESIONAL)
    matricula = models.CharField(max_length=20)
    email = models.EmailField('Correo Electronico')
    domicilio = models.CharField('Domicilio', max_length=200)
    localidad = models.CharField('Localidad', max_length=200)
    telefono = models.CharField('Telefono', max_length=20, default='+549388')
    archivo_dni = models.FileField('Foto DNI', upload_to='inscripciones/dni/')
    archivo_título = models.FileField('Foto Titulo', upload_to='archivos/titulo/')
    info_extra = HTMLField(null=True, blank=True)
    fecha = models.DateTimeField('Fecha Subido', default=timezone.now)
    valido = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True)
    def __str__(self):
        return self.get_profesion_display() + ': ' + self.apellidos + ', ' + self.nombres
    def as_dict(self):
        return {
            'id': self.id,
            'tipo_doc': self.get_tipo_doc_display(),
            'num_doc': self.num_doc,
            'apellidos': self.apellidos,
            'nombres': self.nombres,
            'profesion': self.get_profesion_display(),
            'matrícula': self.endda,
            'email': self.email,
            'telefono': self.telefono,
            'archivo_dni': self.archivo_dni,
            'archivo_título': self.archivo_título,
            'info_extra': self.info_extra,
            'fecha': str(self.fecha),
            'valido': self.valido,
            'disponible': self.disponible,
        }