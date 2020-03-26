#imports de django
from django.apps import AppConfig
#imports del proyecto
from core.functions import agregar_menu

class ConsultasConfig(AppConfig):
    name = 'consultas'
    def ready(self):
        agregar_menu(self)