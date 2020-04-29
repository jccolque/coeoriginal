#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

class InscripcionesConfig(AppConfig):
    name = 'inscripciones'
    def ready(self):
        agregar_menu(self)
        #Lanzamos background jobs
        from .tasks import reintentar_validar
        reintentar_validar(repeat=3600*24)#Cada 12 horas