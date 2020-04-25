#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

class DenunciasConfig(AppConfig):
    name = 'denuncias'
    def ready(self):
        agregar_menu(self)