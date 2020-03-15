#Imports de python
import qrcode
#Realizamos imports de Django
from django.db import models
from django.contrib.auth.models import User
#Imports de paquetes extras
from auditlog.registry import auditlog
#Imports del proyecto:
from coronavirus.settings import MEDIA_ROOT
from core.choices import TIPO_DOCUMENTOS
from core.functions import obtener_organismos

# Create your models here.
class Operador(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="operadores")
    organismo = models.PositiveIntegerField(choices=obtener_organismos(), default=0)
    tipo_doc = models.IntegerField(choices=TIPO_DOCUMENTOS, default=2)
    num_doc = models.IntegerField('Numero de Documento', unique=True)
    fotografia = models.FileField('Fotografia', upload_to='operadores/', null=True, blank=True)
    qrpath = models.CharField('qrpath', max_length=100, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'Operadores'
        permissions = (
            ("menu_operadores", "Puede Acceder al menu de Operadores"),

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
            path = MEDIA_ROOT + '/beneficiarios/qrcode-'+ str(self.num_benef)
            img = qrcode.make(str(self.num_benef))
            img.save(path)
            relative_path = '/archivos/beneficiarios/qrcode-'+ str(self.num_benef)
            self.qrpath = relative_path
            self.save()
            return self.qrpath

#Auditoria
auditlog.register(Operador)