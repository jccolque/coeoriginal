#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

class InformacionConfig(AppConfig):
    name = 'informacion'
    def ready(self):
        agregar_menu(self)
        #Informacion:
        from informacion.tasks import baja_seguimiento, baja_aislamiento
        baja_seguimiento(repeat=3600*12, verbose_name="baja_seguimiento")#Cada 12 horas
        baja_aislamiento(repeat=3600*12, verbose_name="baja_aislamiento")#Cada 12 horas