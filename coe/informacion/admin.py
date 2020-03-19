#Imports Django
from django.contrib import admin
#Imports extras
from django.db import models
from django.forms import CheckboxSelectMultiple
#Imports del proyecto
#Imports de la app
from .models import Archivo
from .models import Enfermedad
from .models import Vehiculo, Individuo
from .models import Situacion
from .models import TipoAtributo, Atributo
from .models import TipoSintoma, Sintoma

#Definimos los inlines:
class SituacionInline(admin.TabularInline):
    model = Situacion
    fk_name = 'individuo'
    extra = 0
    def has_delete_permission(self, request, obj=None):
        return False

class AtributoInline(admin.TabularInline):
    model = Atributo
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
    search_fields = ['nombres', 'apellidos', 'num_doc', ]
    list_filter = ['nacionalidad']
    inlines = [SituacionInline, AtributoInline, SintomaInline, ]
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
admin.site.register(TipoAtributo)
admin.site.register(Archivo, ArchivoAdmin)
admin.site.register(Enfermedad, EnfermedadAdmin)
admin.site.register(Individuo, IndividuoAdmin)
admin.site.register(Vehiculo, VehiculoAdmin)