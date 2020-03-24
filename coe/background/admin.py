#Imports Django
from django.contrib import admin
#Imports Extras
from background_task.models import Task
from background_task.models import CompletedTask
#Imports de la app
from .models import Progress_Links

#Definimos acciones especiales
def inc_priority(modeladmin, request, queryset):
    for obj in queryset:
        obj.priority += 1
        obj.save()
inc_priority.short_description = "priority += 1"

def dec_priority(modeladmin, request, queryset):
    for obj in queryset:
        obj.priority -= 1
        obj.save()
dec_priority.short_description = "priority -= 1"

#Definimos nuestros admins
class TaskAdmin(admin.ModelAdmin):
    display_filter = ['task_name']
    search_fields = ['task_name', 'task_params', ]
    list_display = ['task_name', 'task_params', 'run_at', 'priority', 'attempts', 'has_error', 'locked_by', 'locked_by_pid_running', ]
    actions = [inc_priority, dec_priority]

class CompletedTaskAdmin(admin.ModelAdmin):
    display_filter = ['task_name']
    search_fields = ['task_name', 'task_params', ]
    list_display = ['task_name', 'task_params', 'run_at', 'priority', 'attempts', 'has_error', 'locked_by', 'locked_by_pid_running', ]

class Progress_LinksAdmin(admin.ModelAdmin):
    search_fields = ['tarea', ]


#Desregistramos
admin.site.unregister(Task)
admin.site.unregister(CompletedTask)
#REgistramos modelos
admin.site.register(Task, TaskAdmin)
admin.site.register(CompletedTask, CompletedTaskAdmin)
admin.site.register(Progress_Links, Progress_LinksAdmin)