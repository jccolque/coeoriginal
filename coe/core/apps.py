
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    ADMIN_MENU = []
    ADMIN_MODELS = {}
    def ready(self):
        #Eliminamos todas las tareas previas para iniciar las nuevas
        from background_task.models import Task, CompletedTask
        Task.objects.all().delete()
        CompletedTask.objects.all().delete()