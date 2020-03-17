#Imports Django
from django.contrib import admin
#Imports extras
from django.db import models
from django.forms import CheckboxSelectMultiple
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
#Imports del proyecto
from core.admin import register_hidden_models
#Imports de la app
from .models import Archivo
from .models import Enfermedad
from .models import Vehiculo, Origen, Individuo
from .models import TipoEvento, Evento
from .models import TipoSintoma, Sintoma

#Definimos los inlines:
class EventoInline(admin.TabularInline):
    model = Evento
    fk_name = 'individuo'
    extra = 0
    def has_delete_permission(self, request, obj=None):
        return False   

class SintomaInline(admin.TabularInline):
    model = Sintoma
    fk_name = 'individuo'
    extra = 0
    def has_delete_permission(self, request, obj=None):
        return False

class IndividuoInline(admin.TabularInline):
    model = Individuo
    fk_name = 'individuo'
    extra = 1
    def has_delete_permission(self, request, obj=None):
        return False

#Definimos nuestros modelos administrables:
class ArchivoAdmin(admin.ModelAdmin):
    model = Archivo
    search_fields = ['nombre',]
    list_filter = ['tipo', ]
    def has_delete_permission(self, request, obj=None):
        return False

class EnfermedadAdmin(admin.ModelAdmin):
    model = Individuo
    search_fields = ['nombres', 'sintomas__nombre', ]
    list_filter = ['sintomas']
    def has_delete_permission(self, request, obj=None):
        return False
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

class IndividuoAdmin(admin.ModelAdmin):
    model = Individuo
    search_fields = ['nombres', 'apellidos', 'num_dic', ]
    list_filter = ['nacionalidad']
    inlines = [EventoInline, SintomaInline, ]
    def has_delete_permission(self, request, obj=None):
        return False

class VehiculoAdmin(admin.ModelAdmin):
    model = Vehiculo
    search_fields = ['identificacion',]
    list_filter = ['tipo']
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(TipoSintoma)
admin.site.register(TipoEvento)
admin.site.register(Archivo, ArchivoAdmin)
admin.site.register(Enfermedad, EnfermedadAdmin)
admin.site.register(Individuo, IndividuoAdmin)
admin.site.register(Vehiculo, VehiculoAdmin)