#Imports de Django
from django.contrib import admin
#Imports de la app
from .models import Peticionp

#Definimos Custom Admin
class PeticionPAdmin(admin.ModelAdmin):
    model = Peticionp
    list_filter = ['estado', 'fecha', 'destino']
    search_fields = ['individuos__apellidos', 'individuos__num_doc']

# Register your models here.
admin.site.register(Peticionp, PeticionPAdmin)
