#Imports Django
from django.contrib import admin
#Imports extras

#Imports de la app
from .models import Tarea, Responsable, EventoTarea

#Definimos los inlines:
class ResponsableInline(admin.TabularInline):
    model = Responsable
    fk_name = 'tarea'
    extra = 0
    def has_delete_permission(self, request, obj=None):
        return False

class EventoTareaInline(admin.TabularInline):
    model = EventoTarea
    fk_name = 'tarea'
    extra = 0
    def has_delete_permission(self, request, obj=None):
        return False

#Definimos nuestros modelos administrables:
class TareaAdmin(admin.ModelAdmin):
    model = Tarea
    search_fields = ['nombre',]
    list_filter = ['prioridad']
    inlines = [ResponsableInline, EventoTareaInline]
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(Tarea, TareaAdmin)