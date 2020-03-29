from django.contrib import admin
#Importamos modelos
from .models import Provincia, Departamento, Localidad, Barrio
from .models import Nacionalidad
from .models import Ubicacion
#Definimos inlines
class DepartamentoInline(admin.TabularInline):
    model = Departamento
    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.departamentos.count():
            return 0
        return 1

class LocalidadInline(admin.TabularInline):
    model = Localidad
    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.localidades.count():
            return 0
        return 1

class BarrioInline(admin.TabularInline):
    model = Barrio
    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.barrios.count():
            return 0
        return 1

#Definimos modeficicaciones
class NacionalidadAdmin(admin.ModelAdmin):
    model = Nacionalidad
    search_fields = ['nombre']
    def has_delete_permission(self, request, obj=None):
        return False

class DepartamentoAdmin(admin.ModelAdmin):
    model = Departamento
    search_fields = ['nombre']
    inlines = [LocalidadInline]
    def has_delete_permission(self, request, obj=None):
        return False

class LocalidadAdmin(admin.ModelAdmin):
    model = Localidad
    search_fields = ['nombre']
    list_filter = ['departamento']
    inlines = [BarrioInline]
    def has_delete_permission(self, request, obj=None):
        return False

class BarrioAdmin(admin.ModelAdmin):
    model = Barrio
    search_fields = ['nombre']
    list_filter = ['localidad']
    autocomplete_fields = ['localidad',]
    def has_delete_permission(self, request, obj=None):
        return False

class UbicacionAdmin(admin.ModelAdmin):
    model = Ubicacion
    search_fields = ['nombre', 'localidad']
    list_filter = ['tipo', 'localidad']
    autocomplete_fields = ['localidad',]
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(Provincia, )
admin.site.register(Departamento, DepartamentoAdmin)
admin.site.register(Localidad, LocalidadAdmin)
admin.site.register(Barrio, BarrioAdmin)
admin.site.register(Nacionalidad, NacionalidadAdmin)
admin.site.register(Ubicacion, UbicacionAdmin)
