#imports de django
from django.apps import AppConfig
#imports del proyecto
from core.functions import agregar_menu

class DocumentosConfig(AppConfig):
    name = 'documentos'
    def ready(self):
        agregar_menu(self)