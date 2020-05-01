#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

class GeotrackingConfig(AppConfig):
    name = 'geotracking'
    def ready(self):
        agregar_menu(self)
        #Tareas Background:
        from geotracking.tasks import geotrack_sin_actualizacion, finalizar_geotracking
        geotrack_sin_actualizacion(repeat=3600, verbose_name="geotrack_sin_actualizacion")#Cada una hora
        finalizar_geotracking(repeat=3600*12, verbose_name="finalizar_geotracking")#Cada 12 horas