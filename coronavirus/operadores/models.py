#Imports de python
import qrcode
#Realizamos imports de Django
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
#Imports de paquetes extras
from auditlog.registry import auditlog
#Imports del proyecto:
from coronavirus.settings import MEDIA_ROOT
from core.choices import TIPO_DOCUMENTOS
from core.api import obtener_organismos
#improts de la app
from .choices import TIPO_EVENTO

# Create your models here.
class Operador(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="operadores")
    organismo = models.PositiveIntegerField(choices=obtener_organismos(), default=0)
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.IntegerField('Numero de Documento', unique=True)
    telefono = models.CharField('Telefono', max_length=20, default='+549388')
    fotografia = models.FileField('Fotografia', upload_to='operadores/', null=True, blank=True)
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'Operadores'
        permissions = (
            ("menu_operadores", "Puede Acceder al menu de Operadores"),
            ("listar_operadores", "Puede ver el Listado de Operadores"),
            ("crear_operador", "Puede Crear Operadores"),
            ("modificar_operador", "Puede Modificar Operadores"),
            ("auditar_operadores", "Auditar Acciones de otros Operadores"),
            ("ver_credencial", "Ver Credencial de Operador"),

            ("control_asistencia", "Control de Ingreso Fisico de los Operadores"),
            
            ("menu_inventario", "Puede Acceder al menu Inventario"),

            ("menu_tareas", "Puede Acceder al menu de Tareas"),

            ("menu_informacion", "Puede Acceder al menu de Informacion"),
            ("archivos_pendientes", "Puede ver listado archivos pendientes."),
            ("ver_archivos", "Puede ver archivos."),
            ("subir_archivos", "Puede subir archivos."),

            ("menu_actas", "Puede Acceder al menu de Actas"),

            ("administrador", "Puede administrar Usuarios."),
        )   
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

#Auditoria
auditlog.register(Operador)