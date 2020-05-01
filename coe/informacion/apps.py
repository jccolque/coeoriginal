#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from core.functions import agregar_menu

class InformacionConfig(AppConfig):
    name = 'informacion'
    def ready(self):
        agregar_menu(self)
        #Informacion:
        try:
            from background_task.models import Task
            if not Task.objects.filter(verbose_name="baja_seguimiento").exists():
                from informacion.tasks import baja_seguimiento
                baja_seguimiento(repeat=3600*12, verbose_name="baja_seguimiento")#Cada 12 horas
            if not Task.objects.filter(verbose_name="baja_aislamiento").exists():
                from informacion.tasks import baja_aislamiento
                baja_aislamiento(repeat=3600*12, verbose_name="baja_aislamiento")#Cada 12 horas
            if not Task.objects.filter(verbose_name="devolver_domicilio").exists():
                from informacion.tasks import devolver_domicilio
                devolver_domicilio(repeat=3600*8, verbose_name="devolver_domicilio")#Cada 12 horas
            if not Task.objects.filter(verbose_name="baja_cuarentena").exists():
                from informacion.tasks import baja_cuarentena
                baja_cuarentena(repeat=3600*8, verbose_name="baja_cuarentena")#Cada 12 horas
        except OperationalError:
            pass  #  Por si no existe