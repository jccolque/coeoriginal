#Imports de Django
from django.db import models
from django.utils import timezone
#Imports extras
from tinymce.models import HTMLField
#Imports del proyecto
from georef.models import Localidad, Ubicacion
from informacion.models import Individuo
from operadores.models import Operador
#Imports de la app
from .choices import TIPO_INSCRIPTO, ESTADO_INSCRIPTO
from .choices import GRUPO_SANGUINEO, TIPO_PROFESIONAL, TIPO_DISPOSITIVO
from .tokens import token_inscripcion

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

class Capacitacion(models.Model):
    orden = models.SmallIntegerField(verbose_name="Orden de Visualizacion")
    tipo = models.CharField(choices=TIPO_INSCRIPTO, max_length=2, default='VS')
    nombre = models.CharField('Nombre Capacitacion', max_length=100)
    link = models.URLField('Link')
    class Meta:
        ordering = ['orden', ]
    def __str__(self):
        return self.get_tipo_display() + ': ' + self.nombre

#Modelos primarios
class Inscripcion(models.Model):
    tipo_inscripto = models.CharField(choices=TIPO_INSCRIPTO, max_length=2, default='PS')
    estado = models.IntegerField(choices=ESTADO_INSCRIPTO, default=0)
    individuo = models.ForeignKey(Individuo, on_delete=models.CASCADE, null=True, blank=True, related_name="voluntariados")
    profesion = models.IntegerField('Profesion', choices=TIPO_PROFESIONAL, null=True, blank=True)
    matricula = models.CharField(max_length=20, null=True, blank=True)
    oficio = models.CharField("Profesion u Oficio", max_length=100, null=True, blank=True)
    frente_dni = models.FileField('Foto Frente DNI', upload_to='inscripciones/documentos/', null=True, blank=True)
    reverso_dni = models.FileField('Foto Reverso DNI', upload_to='inscripciones/documentos/', null=True, blank=True)
    archivo_titulo = models.FileField('Foto Titulo', upload_to='inscripciones/titulo/', null=True, blank=True)
    info_extra = HTMLField(null=True, blank=True)
    #grupo_sanguineo = models.IntegerField('Grupo Sanguineo', choices=GRUPO_SANGUINEO, null=True, blank=True)
    #dona_sangre = models.BooleanField(default=False, null=True, blank=True)
    tiene_internet = models.BooleanField(default=False, null=True, blank=True)
    capacitaciones = models.ManyToManyField(Capacitacion)
    fecha = models.DateTimeField('Fecha Inscripcion', default=timezone.now)
    valido = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True)
    def chequear_estado(self):
        if self.estado == 0:#Inscripcion Iniciada
            if self.individuo.fotografia and self.get_frente_dni() and self.get_reverso_dni():
                self.estado = 1
                self.save()
        if self.estado == 1:#Inscripcion Terminada - Esperando Aprobacion
            #Automatizamos por orden de desarrollo humano
            self.estado = 2
            self.save()
        if self.estado == 2:#Capacitaciones
            if self.capacitaciones.count() == Capacitacion.objects.filter(tipo=self.tipo_inscripto).count():
                self.estado = 3
                self.save()
        if self.estado == 3:#Turno Para firmar Acuerdo Basico Pedido
            if self.turnos.exists():
                self.estado = 4
                self.save()
    def get_frente_dni(self):
        doc = self.individuo.documentos.filter(tipo='DI', aclaracion__icontains='FRENTE').last()
        if doc:
            return doc.archivo
    def get_reverso_dni(self):
        doc = self.individuo.documentos.filter(tipo='DI', aclaracion__icontains='REVERSO').last()
        if doc:
            return doc.archivo
    def get_titulo(self):
        doc = self.individuo.documentos.filter(tipo='TP').last()
        if doc:
            return doc.archivo
    def __str__(self):
        try:
            return self.individuo.apellidos + ', ' + self.individuo.nombres
        except:
            return "Sin Individuo"
    def turno_activo(self):
        return self.turnos.filter(fecha__gt=timezone.now()).exists()
    def as_dict(self):
        return {
            'id': self.id,
            'tipo_inscripto': self.tipo_inscripto,
            'individuo': self.individuo.id,
            'profesion': self.get_profesion_display(),
            'oficio': self.oficio,
            'matrícula': self.matricula,
            'frente_dni': str(self.frente_dni),
            'reverso_dni': str(self.reverso_dni),
            'archivo_título': str(self.archivo_titulo),
            'info_extra': self.info_extra,
            'fecha': str(self.fecha),
            'valido': self.valido,
            'disponible': self.disponible,
        }

class TareaElegida(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name="tareas")
    inscripto = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name="tareas")

class Dispositivo(models.Model):
    inscripto = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name="dispositivos")
    tipo = models.CharField('Tipo Dispositivo', choices=TIPO_DISPOSITIVO, max_length=2)

class Turno(models.Model):
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, related_name='turnos_inscripciones')
    fecha = models.DateTimeField("Dia y Hora del Turno", default=timezone.now)
    inscripto = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, null=True, blank=True, related_name="turnos")
    class Meta:
        ordering = ['fecha']

class EmailsInscripto(models.Model):
    inscripto = models.ForeignKey(Inscripcion, on_delete=models.CASCADE, related_name="emails_enviados")
    fecha = models.DateTimeField('Fecha de Envio', default=timezone.now)
    asunto = models.CharField('Asunto', max_length=100)
    cuerpo = models.CharField('Asunto', max_length=1000)
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="inscripcion_emailsenviados")

#Voluntarios Estudiantiles
class ProyectoEstudiantil(models.Model):
    #Proyecto
    nombre = models.CharField('Nombre del Proyecto', max_length=200)
    documento = models.FileField('Documento del Proyecto', upload_to='inscripciones/estudiantil/', null=True, blank=True)
    descripcion = HTMLField()
    email_contacto = models.EmailField('Correo Electronico de Contacto')
    #Institucion
    escuela_nombre = models.CharField('Nombre de la Escuela', max_length=200)
    escuela_localidad = models.CharField('Localidad', max_length=200)
    escuela_telefono = models.CharField('Telefono Institucion', max_length=50)
    escuela_aval = models.FileField('Aval Institucional', upload_to='inscripciones/estudiantil/', null=True, blank=True)
    #Reponsable
    responsable = models.ForeignKey(Individuo, on_delete=models.CASCADE, null=True, blank=True, related_name="responsable_estudiantil")
    #Voluntarios
    voluntarios = models.ManyToManyField(Individuo, related_name='voluntario_estudiantil')
    #Campos internos
    token = models.CharField('Token', max_length=50, default=token_inscripcion, unique=True)
    estado = models.IntegerField(choices=ESTADO_INSCRIPTO, default=0)
    fecha = models.DateTimeField('Fecha de registro', default=timezone.now)
    