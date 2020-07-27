#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

#Configuramos nuestra app
class OperadoresConfig(AppConfig):
    name = 'operadores'
    def ready(self):
        agregar_menu(self)
        from .signals import asignar_individuo