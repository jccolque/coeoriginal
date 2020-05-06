#Imports de python
import qrcode
#Realizamos imports de Django
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
#Imports de paquetes extras
from auditlog.registry import auditlog
from tinymce.models import HTMLField
#Imports del proyecto:
from coe.settings import MEDIA_ROOT, LOADDATA
from coe.constantes import NOIMAGE
from core.choices import TIPO_DOCUMENTOS
#improts de la app
from .choices import TIPO_EVENTO, NIVELES_SEGURIDAD

# Create your models here.
class SubComite(models.Model):
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    descripcion = HTMLField()
    activo = models.BooleanField(default=True)
    class Meta:
        verbose_name = 'Modulo'
        verbose_name_plural = 'Modulos'
        ordering = ['nombre', ]
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
        }
    def cant_miembros(self):
        return self.operadores.count()
    def cant_tareas_terminadas(self):
        cant = 0
        for tarea in self.tareas.all():
            evento = [t for t in tarea.eventos.all()][-1]
            if evento.accion == 'E':
                    cant+=1
        return cant
    def cant_tareas_pendientes(self):
        cant = 0
        for tarea in self.tareas.all():
            evento = [t for t in tarea.eventos.all()][-1]
            if not evento.accion == 'E':
                    cant+=1
        return cant
    def tareas_pendientes(self):
        return self.tareas.exclude(eventos__accion="E")

class Operador(models.Model):
    subcomite = models.ForeignKey(SubComite, on_delete=models.SET_NULL, null=True, related_name="operadores")
    nivel_acceso = models.CharField("Acceso de Seguridad", max_length=1, choices=NIVELES_SEGURIDAD, default='B')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="operadores")
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.CharField('Numero de Documento', unique=True, max_length=100)
    apellidos = models.CharField('Apellidos', max_length=100)
    nombres  = models.CharField('Nombres', max_length=100)
    email = models.EmailField('Correo Electronico')
    telefono = models.CharField('Telefono', max_length=20, default='+549388')
    fotografia = models.FileField('Fotografia', upload_to='operadores/', null=True, blank=True)
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'Operadores'
        ordering = ['apellidos', 'nombres']
        permissions = (
            #Home
            ("menu_core", "Puede Acceder al Sistema Principal"),
            ("consultas", "Puede Acceder al Sistema de Consultas"),
            #Operadores:
            ("menu_operadores", "Puede Acceder al menu de Operadores"),
            ("subcomites", "Puede Crear/Modificar SubComites"),
            ("operadores", "Puede Crear/Modificar Operadores"),
            ("auditar_operadores", "Puede Auditar Operadores"),
            #Georef
            ("menu_georef", "Puede Administrar Informacion Geografica"),
            #Inventario
            ("menu_inventario", "Puede Acceder al menu Inventario"),
            #Tareas:
            ("menu_tareas", "Puede Acceder al menu de Tareas"),
            #Informacion:
            ("menu_informacion", "Puede Acceder al menu de Informacion"),
            ("archivos", "Puede Crear Archivos."),
            ("vehiculos", "Puede Crear/Modificar Informacion de Vehiculo."),
            ("individuos", "Puede Crear/Modificar Informacion de Individuos."),
            #GeoTracking
            ("geotracking", "Puede Monitorear el Tracking de Individuos."),
            ("geotracking_admin", "Puede Administrar Sistema de GeTracking."),
            #Permisos:
            ("permisos", "Puede administrar los permisos de Circulacion."),
            ("fronteras", "Personal de Control en Fronteras."),
            #Graficos:
            ("menu_graficos", "Puede Administrar los Graficos"),
            #Actas:
            ("menu_actas", "Puede Acceder al menu de Actas"),
            #Documentos
            ("menu_documentos", "Puede Acceder al menu de Documentos"),
            ("documentos", "Puede Administrar Documentos"),
            #Inscripciones:
            ("menu_inscripciones", "Puede Acceder al menu de Inscripciones"),
            #Reportes
            ("reportes", "Acceso a todos los reportes del sistema"),
            #Wservices
            ("wservices", "Acceso a todos los reportes del sistema"),
            #Especiales
            ("administrador", "Puede administrar Usuarios."),
        )
    def __str__(self):
        return self.apellidos + ', ' + self.nombres
    def as_dict(self):
        return {
            'id': self.id,
            'subcomite': str(self.subcomite),
            'usuario': str(self.usuario),
            'tipo_doc': self.tipo_doc,
            'num_doc': self.num_doc,
            'apellidos': self.apellidos,
            'nombres': self.nombres,
            'email': self.email,
            'telefono': self.telefono,
            'fotografia': str(self.fotografia),
            'qrpath': str(self.qrpath),
        }
    def get_foto(self):
        if self.fotografia:
            return self.fotografia.url
        else:
            return NOIMAGE
    def get_qrimage(self):
        if self.qrpath:
            return self.qrpath
        else:
            path = MEDIA_ROOT + '/operadores/qrcode-'+ str(self.num_doc)
            img = qrcode.make(str(self.num_doc))
            img.save(path)
            relative_path = '/archivos/operadores/qrcode-'+ str(self.num_doc)
            self.qrpath = relative_path
            self.save()
            return self.qrpath
    def tareas_pendientes(self):
        return [r.tarea for r in self.responsables.all().exclude(tarea__eventos__accion='E')]

class EventoOperador(models.Model):
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, null=True, blank=True, related_name="asistencia")
    tipo = models.CharField('Tipo de Evento', max_length=1, choices=TIPO_EVENTO, default='I')
    fecha = models.DateTimeField('Fecha', default=timezone.now)
    def __str__(self):
        return str(self.operador) + ': ' + self.get_tipo_display() + ' - ' + str(self.fecha)
    def as_dict(self):
        return {
            'id': self.id,
            'operador_id': self.operador.id,
            'operador': str(self.operador),
            'tipo': self.get_tipo_display(),
            'fecha': str(self.fecha),
        }

if not LOADDATA:
    #Auditoria
    auditlog.register(SubComite)
    auditlog.register(Operador)
    auditlog.register(User)
