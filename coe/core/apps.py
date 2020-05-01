
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    ADMIN_MENU = []
    ADMIN_MODELS = {}
    def ready(self):
        #Eliminamos todas las tareas previas para iniciar las nuevas
        try:
            from background_task.models import Task, CompletedTask
            Task.objects.all().delete()
            CompletedTask.objects.all().delete()
        except:
            pass  #  No ejecutar si las tablas no estan listas