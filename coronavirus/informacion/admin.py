#Imports Django
from django.contrib import admin
#Imports extras
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
#Imports del proyecto
from core.admin import register_hidden_models
#Imports de la app
from .models import Archivo
from .models import Vehiculo, Origen, Individuo
from .models import TipoSintoma, Sintoma


#Definimos los inlines:
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

class IndividuoAdmin(admin.ModelAdmin):
    model = Individuo
    search_fields = ['nombres', 'apellidos', 'num_dic', ]
    list_filter = ['nacionalidad']
    inlines = [SintomaInline, ]
    def has_delete_permission(self, request, obj=None):
        return False

class VehiculoAdmin(admin.ModelAdmin):
    model = Vehiculo
    search_fields = ['identificacion',]
    list_filter = ['tipo']
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
register_hidden_models(TipoSintoma)
admin.site.register(Archivo, ArchivoAdmin)
admin.site.register(Individuo, IndividuoAdmin)
admin.site.register(Vehiculo, VehiculoAdmin)