#Imports de python
import logging
import traceback
#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from coe.settings import LOADDATA
from core.functions import agregar_menu

class GeotrackingConfig(AppConfig):
    name = 'geotracking'
    def ready(self):
        agregar_menu(self)
        #BackgroundJobs
        from background.functions import inicializar_background_job
        from .tasks import geotrack_sin_actualizacion
        inicializar_background_job(geotrack_sin_actualizacion, 4, 'geotrack_sin_actualizacion')
        #Señales
        if not LOADDATA:
            from .signals import asignar_geoperador
            from .signals import inicio_seguimiento
