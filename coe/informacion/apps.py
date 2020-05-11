#Imports de python
import logging
import traceback
#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from coe.settings import DEBUG, LOADDATA
from core.functions import agregar_menu

class InformacionConfig(AppConfig):
    name = 'informacion'
    def ready(self):
        agregar_menu(self)
        #Cargamos signals
        if not LOADDATA:
            #Señales
            from .signals import estado_inicial
            from .signals import situacion_actual
            from .signals import domicilio_actual
            from .signals import relacion_domicilio
            from .signals import crear_relacion_inversa
            from .signals import eliminar_relacion_inversa
            from .signals import relacion_vehiculo
            from .signals import relacionar_situacion
            from .signals import afectar_relacionados
            from .signals import aislar_individuo
            #Seguimientos
            from seguimiento.signals import iniciar_seguimiento
            from seguimiento.signals import poner_en_seguimiento
            from seguimiento.signals import seguimiento_mental
            from seguimiento.signals import cargo_signosvitales
            from seguimiento.signals import cargo_documento
        # #Background Jobs
        # try:
        #     if not DEBUG:
        #         from background_task.models import Task
        #         if not Task.objects.filter(verbose_name="baja_aislamiento").exists():
        #             from informacion.tasks import baja_aislamiento
        #             baja_aislamiento(repeat=3600*12, verbose_name="baja_aislamiento")#Cada 12 horas
        #         if not Task.objects.filter(verbose_name="devolver_domicilio").exists():
        #             from informacion.tasks import devolver_domicilio
        #             devolver_domicilio(repeat=3600*8, verbose_name="devolver_domicilio")#Cada 12 horas
        #         if not Task.objects.filter(verbose_name="baja_cuarentena").exists():
        #             from informacion.tasks import baja_cuarentena
        #             baja_cuarentena(repeat=3600*8, verbose_name="baja_cuarentena")#Cada 12 horas
        # except OperationalError:
        #     logger = logging.getLogger("tasks")
        #     logger.info("Falla: "+str(traceback.format_exc()))