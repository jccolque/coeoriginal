#Imports de python
import logging
import traceback
#Imports Django
from django.apps import AppConfig
from django.db import OperationalError
#Imports del Proyecto
from coe.settings import DEBUG, LOADDATA
from core.functions import agregar_menu

class InformacionConfig(AppConfig):
    name = 'informacion'
    def ready(self):
        agregar_menu(self)
        #Cargamos signals
        if not LOADDATA:
            #Señales
            from .signals import estado_inicial
            from .signals import situacion_actual
            from .signals import domicilio_actual
            from .signals import relacion_domicilio
            from .signals import crear_relacion_inversa
            from .signals import eliminar_relacion_inversa
            from .signals import relacionar_situacion_nueva
            from .signals import afectar_relacionados
            from .signals import aislar_individuo
            from .signals import aislamiento_domiciliario