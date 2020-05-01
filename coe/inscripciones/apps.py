#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from core.functions import agregar_menu

class InscripcionesConfig(AppConfig):
    name = 'inscripciones'
    def ready(self):
        agregar_menu(self)
        #Lanzamos background jobs
        try:
            from background_task.models import Task
            if not Task.objects.filter(verbose_name="reintentar_validar").exists():
                from .tasks import reintentar_validar
                reintentar_validar(repeat=3600*24, verbose_name="reintentar_validar")#Cada 24 horas
        except OperationalError:
            pass  # Por si no existe