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
            from .signals import iniciar_seguimiento
            from .signals import descartar_sospechoso
            from .signals import poner_en_seguimiento
            from .signals import buscar_controlador
            from .signals import cargo_signosvitales
            from .signals import cargo_documento