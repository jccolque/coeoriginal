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
            from .signals import recuperar_seguimiento
            from .signals import iniciar_seguimiento
            from .signals import seguimiento_urgente
            from .signals import evolucionar_sospechoso
            from .signals import descartar_sospechoso
            from .signals import confirmar_sospechoso
            from .signals import poner_en_seguimiento
            from .signals import atributo_vigilancia
            from .signals import cargo_signosvitales
            from .signals import sin_telefono
            from .signals import finalizar_seguimiento
            #Operativo
            from .signals import operativo_get_individuo