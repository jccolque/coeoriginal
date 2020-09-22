#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

class TableroConfig(AppConfig):
    name = 'tablero'
    def ready(self):
        agregar_menu(self)