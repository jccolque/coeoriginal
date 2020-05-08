#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from core.functions import agregar_menu

class SeguimientoConfig(AppConfig):
    name = 'seguimiento'
    def ready(self):
        agregar_menu(self)