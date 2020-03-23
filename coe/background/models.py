#Imports Django
from django.db import models
from django.utils import timezone
#Imports extras
from background_task.models import Task as bg_Tasks
from background_task.models_completed import CompletedTask as bg_CompletedTask

# Create your models here.
class Progress_Links(models.Model):
    tarea = models.CharField('Tarea', max_length=50)
    inicio = models.DateTimeField(default=timezone.now)
    progress_url = models.URLField('Web', blank=True, null=True)
    def __str__(self):
        return self.tarea + ': ' + str(self.inicio)
    def en_cola(self):
        return bg_Tasks.objects.filter(queue__icontains=self.tarea)
    def terminadas(self):
        return bg_CompletedTask.objects.filter(queue__icontains=self.tarea)
    def total(self):
        return self.en_cola().count() + self.terminadas().count()
    def estado(self):
        cant_prog = bg_Tasks.objects.filter(queue__icontains=self.tarea).count()
        cant_term = bg_CompletedTask.objects.filter(queue__icontains=self.tarea).count()
        total = cant_prog + cant_term
        porcentaje = ( 100 / total) * cant_term
        if porcentaje == '100':
            return 'Terminada'
        elif porcentaje > 0:
            return 'En proceso '+str(porcentaje)+'%'
        else:
            return 'En Espera'