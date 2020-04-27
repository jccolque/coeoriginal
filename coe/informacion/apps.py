#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

class InformacionConfig(AppConfig):
    name = 'informacion'
    def ready(self):
        agregar_menu(self)
        #Tareas recursivas:
        from .tasks import baja_seguimiento
        baja_seguimiento(repeat=3600*12)#Cada 12 horas