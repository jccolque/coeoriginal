#Imports Django
from django.contrib import admin
#Imports de la app
from .models import Inscripto

#Definimos nuestros modelos administrables:
class InscriptoAdmin(admin.ModelAdmin):
    model = Inscripto
    search_fields = ['num_doc', 'apellidos', 'nombres',]
    list_filter = ['profesion']

# Register your models here.
admin.site.register(Inscripto, InscriptoAdmin)