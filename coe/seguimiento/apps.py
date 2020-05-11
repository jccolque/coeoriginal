#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from coe.settings import DEBUG, LOADDATA
from core.functions import agregar_menu

class SeguimientoConfig(AppConfig):
    name = 'seguimiento'
    def ready(self):
        agregar_menu(self)
        #Cargamos signals
        if not LOADDATA:
            from .signals import seguimiento_actual
        # #Lanzamos background jobs
        # try:
        #     if not DEBUG:
        #         from background_task.models import Task
        #         if not Task.objects.filter(verbose_name="baja_seguimiento").exists():
        #             from seguimiento.tasks import baja_seguimiento
        #             baja_seguimiento(repeat=3600*12, verbose_name="baja_seguimiento")#Cada 12 horas
        # except OperationalError:
        #     pass  #  Por si no existe