#Imports de python
import logging
import traceback
#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from coe.settings import DEBUG
from core.functions import agregar_menu

class InscripcionesConfig(AppConfig):
    name = 'inscripciones'
    def ready(self):
        agregar_menu(self)
        #BackgroundJobs
        from background.functions import inicializar_background_job
        from .tasks import reintentar_validar
        inicializar_background_job(reintentar_validar, 24, 'reintentar_validar')