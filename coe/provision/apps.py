#Imports Django
from django.apps import AppConfig
from django.db import OperationalError

#Imports del Proyecto
from coe.settings import DEBUG, LOADDATA
from core.functions import agregar_menu


class ProvisionConfig(AppConfig):
    name = 'provision'
    def ready(self):
        agregar_menu(self)
    

        