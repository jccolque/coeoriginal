#Imports de Django
from django.contrib import admin
#Imports de la app
from .models import Permiso
from .models import IngresoProvincia

#Definimos Custom Admin
class IngresoProvinciaAdmin(admin.ModelAdmin):
    model = IngresoProvincia
    list_filter = ['tipo', 'fecha_llegada', 'origen']
    search_fields = ['individuos__apellido', 'individuos__num_doc']

# Register your models here.
admin.site.register(Permiso)
admin.site.register(IngresoProvincia, IngresoProvinciaAdmin)