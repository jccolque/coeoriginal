#Imports Django
from django.contrib import admin
#Imports extras
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
#Imports de la app
from .models import Acta, Participes, EventoParticipe

#Definimos los inlines:
class EventoParticipeInline(NestedStackedInline):
    model = EventoParticipe
    fk_name = 'participe'
    extra = 1
    def has_delete_permission(self, request, obj=None):
        return False

class ParticipesInline(NestedStackedInline):
    model = Participes
    fk_name = 'acta'
    inlines = [EventoParticipeInline]
    extra = 1
    def has_delete_permission(self, request, obj=None):
        return False

#Definimos nuestros modelos administrables:
class ActaAdmin(NestedModelAdmin):
    model = Acta
    search_fields = ['nombre',]
    list_filter = ['tipo']
    inlines = [ParticipesInline]
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(Acta, ActaAdmin)