#Imports Django
from django.contrib import admin
#Imports extras
#Imports de la app
from .models import Acta, Participes

#Definimos los inlines:
class ParticipesInline(admin.TabularInline):
    model = Participes
    fk_name = 'acta'
    extra = 1
    def has_delete_permission(self, request, obj=None):
        return False

#Definimos nuestros modelos administrables:
class ActaAdmin(admin.ModelAdmin):
    model = Acta
    search_fields = ['nombre',]
    list_filter = ['tipo']
    inlines = [ParticipesInline]
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(Acta, ActaAdmin)