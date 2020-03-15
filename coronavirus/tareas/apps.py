#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

#Configuramos nuestra app
class TareasConfig(AppConfig):
    name = 'tareas'
    def ready(self):
        agregar_menu(self)
