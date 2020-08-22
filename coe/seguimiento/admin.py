#Imports de Django
from django.contrib import admin
#Imports de la app
from .models import Muestra
from .models import DatosGis

#Definimos Custom Admin
class MuestraAdmin(admin.ModelAdmin):
    model = Muestra
    list_filter = ['estado', 'fecha_muestra', 'prioridad']
    search_fields = ['individuos__apellido', 'individuos__num_doc']

class DatosGisAdmin(admin.ModelAdmin):
    model = DatosGis

# Register your models here.
admin.site.register(Muestra, MuestraAdmin)
admin.site.register(DatosGis, DatosGisAdmin)