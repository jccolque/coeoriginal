#Imports Django
from django.apps import AppConfig
#Imports del Proyecto
from core.functions import agregar_menu

class GeotrackingConfig(AppConfig):
    name = 'geotracking'
    def ready(self):
        agregar_menu(self)
        #Tareas Background:
        from background_task.models import Task
        if not Task.objects.filter(verbose_name="geotrack_sin_actualizacion").exists():
            from geotracking.tasks import geotrack_sin_actualizacion
            geotrack_sin_actualizacion(repeat=3600, verbose_name="geotrack_sin_actualizacion")#Cada una hora
        if not Task.objects.filter(verbose_name="finalizar_geotracking").exists():
            from geotracking.tasks import finalizar_geotracking
            finalizar_geotracking(repeat=3600*12, verbose_name="finalizar_geotracking")#Cada 12 horas