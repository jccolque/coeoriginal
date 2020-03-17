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
from coe.settings import MEDIA_ROOT
from core.choices import TIPO_DOCUMENTOS
#from core.api import obtener_organismos
#improts de la app
from .choices import TIPO_EVENTO, NIVELES_SEGURIDAD

# Create your models here.
class SubComite(models.Model):
    nombre = models.CharField('Nombre', max_length=50)
    descripcion = HTMLField()
    activo = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre
    def as_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombred,
            'descripcion': self.descripcion,
            'activo': self.activo,
        }
    def cant_miembros(self):
        return self.operadores.count()
    def cant_tareas_terminadas(self):
        return self.tareas.filter(eventos__accion="E").count()
    def cant_tareas_pendientes(self):
        return self.tareas.exclude(eventos__accion="E").count()

class Operador(models.Model):
    #organismo = models.PositiveIntegerField(choices=obtener_organismos(), default=0)
    subcomite = models.ForeignKey(SubComite, on_delete=models.SET_NULL, null=True, blank=True, related_name="operadores")
    nivel_acceso = models.CharField("Acceso de Seguridad", max_length=1, choices=NIVELES_SEGURIDAD, default='B')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="operadores")
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.IntegerField('Numero de Documento', unique=True)
    apellidos = models.CharField('Apellidos', max_length=50)
    nombres  = models.CharField('Nombres', max_length=50)
    email = models.EmailField('Correo Electronico')
    telefono = models.CharField('Telefono', max_length=20, default='+549388')
    fotografia = models.FileField('Fotografia', upload_to='operadores/', null=True, blank=True)
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'Operadores'
        permissions = (
            #Operadores:
            ("menu_operadores", "Puede Acceder al menu de Operadores"),
            ("ver_subcomites", "Puede ver SubComites"),
            ("crear_subcomite", "Puede Crear Subcomites"),
            ("listar_operadores", "Puede ver el Listado de Operadores"),
            ("crear_operador", "Puede Crear Operadores"),
            ("modificar_operador", "Puede Modificar Operadores"),
            ("ver_credencial", "Ver Credencial de Operador"),
            ("control_asistencia", "Control de Ingreso Fisico de los Operadores"),
            ("auditar_operadores", "Auditar Acciones de otros Operadores"),
            #Inventario
            ("menu_inventario", "Puede Acceder al menu Inventario"),
            
            #Tareas:
            ("menu_tareas", "Puede Acceder al menu de Tareas"),
            ("ver_tarea", "Puede ver listado de Tareas"),
            ("crear_tarea", "Puede crear Tareas"),
            ("asignar_responsable", "Puede Agregar Responsables a las Tareas"),
            ("cargar_evento", "Puede cargar_evento a las Tareas"),
            #Informacion:
            ("menu_informacion", "Puede Acceder al menu de Informacion"),
            ("archivos_pendientes", "Puede ver listado archivos pendientes."),
            ("ver_archivos", "Puede ver archivos."),
            ("subir_archivos", "Puede subir archivos."),
            ("procesar_archivos", "Puede Marcar Archivos como Procesado."),
            ("ver_vehiculo", "Puede Ver Informacion de Vehiculo."),
            ("cargar_vehiculo", "Puede Cargar Informacion de Vehiculo."),
            ("ver_individuo", "Puede Ver Informacion de Individuos."),
            ("cargar_individuo", "Puede Cargar Informacion de Individuos."),
            #Actas:
            ("menu_actas", "Puede Acceder al menu de Actas"),
            ("ver_acta", "Puede Ver Actas"),
            ("crear_acta", "Puede Crear Actas"),

            ("administrador", "Puede administrar Usuarios."),
        )
    def __str__(self):
        return self.apellidos + ', ' + self.nombres
    def as_dict(self):
        return {
            'id': self.id,
            'organismo': self.get_organismo_display(),
            'subcomite': self.subcomite,
            'usuario_id': self.usuario.id,
            'usuario_username': self.usuario.username,
            'tipo_doc': self.tipo_doc,
            'num_doc': self.num_doc,
            'telefono': self.telefono,
            'fotografia': self.fotografia,
            'qrpath': self.qrpath,
        }
    def get_foto(self):
        if self.fotografia:
            return self.fotografia.url
        else:
            return 'NOIMAGE'
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
            'tipo': self.get_tipo_display,
            'fecha': self.fecha,
        }
#Auditoria
auditlog.register(SubComite)
auditlog.register(Operador)
auditlog.register(User)