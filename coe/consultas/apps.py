#imports de django
from django.apps import AppConfig
#imports del proyecto
from core.functions import agregar_menu
from coe.settings import LOADDATA

class ConsultasConfig(AppConfig):
    name = 'consultas'
    def ready(self):
        agregar_menu(self)
        #Cargamos signals
        if not LOADDATA:
            from .signals import asignar_denuncia