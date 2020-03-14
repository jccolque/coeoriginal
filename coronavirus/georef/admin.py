from django.contrib import admin
from django.contrib.gis import admin as gis_admin
#Importamos modelos
from .models import Provincia, Departamento, Localidad, Barrio

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
class DepartamentoAdmin(admin.ModelAdmin):
    model = Departamento
    search_fields = ['nombre']
    inlines = [LocalidadInline]

class LocalidadAdmin(admin.ModelAdmin):
    model = Localidad
    search_fields = ['nombre']
    list_filter = ['departamento']
    inlines = [BarrioInline]

class BarrioAdmin(admin.ModelAdmin):
    model = Barrio
    search_fields = ['nombre']
    list_filter = ['localidad']

# Register your models here.
admin.site.register(Provincia, )
admin.site.register(Departamento, DepartamentoAdmin)
admin.site.register(Localidad, LocalidadAdmin)
admin.site.register(Barrio, BarrioAdmin)
