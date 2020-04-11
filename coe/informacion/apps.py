#Imports Django
import copy
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

class InformacionConfig(AppConfig):
    name = 'informacion'
    def ready(self):
        agregar_menu(self)
        #Fabricamos un menus virtuales
        geo = copy.copy(self)
        geo.name = "geotracking"
        agregar_menu(geo)
        #Permisos
        permisos = copy.copy(self)
        permisos.name = "permisos"
        agregar_menu(permisos)