#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from coe.settings import DEBUG, LOADDATA

class AppConfigure(AppConfig):
    name = 'app'
    def ready(self):
        #Cargamos signals
        if not LOADDATA:
            #Señales
            from .signals import enviar_push
