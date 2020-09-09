#imports de django
from django.apps import AppConfig
#imports del proyecto
from core.functions import agregar_menu

class GeorefConfig(AppConfig):
    name = 'georef'
    def ready(self):
        agregar_menu(self)
        #Inicializacion de georeferencias:
        try:
            from .models import Localidad
            if not Localidad.objects.exists():
                from background_task.models import Task
                from background.functions import inicializar_background_job
                from .tasks import obtener_localidades_infra_gob
                inicializar_background_job(obtener_localidades_infra_gob, Task.NEVER, 'obtener_localidades_infra_gob')
        except:
            print("No se pudo inicializar georeferencias")