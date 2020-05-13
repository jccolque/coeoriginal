#Imports de python
import logging
import traceback
#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from coe.settings import LOADDATA

class CoreConfig(AppConfig):
    name = 'core'
    ADMIN_MENU = []
    ADMIN_MODELS = {}
    def ready(self):
        #Background Jobs
        from background.functions import limpiar_background_viejas
        limpiar_background_viejas()
        #Señales
        if not LOADDATA:
            from .signals import enviar_mail_new_user