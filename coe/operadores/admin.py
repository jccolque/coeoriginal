#Imports Django
from django.contrib import admin
#Imports extras

#Imports de proyecto
#Imports de la app
from .models import SubComite, Operador

#Definimos nuestros modelos administrables:
class SubComiteAdmin(admin.ModelAdmin):
    model = SubComite
    search_fields = ['nombre',]

class OperadorAdmin(admin.ModelAdmin):
    model = Operador
    list_filter = ['subcomite', 'nivel_acceso']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'num_doc']
    readonly_fields = ['qrpath']

# Register your models here.
admin.site.register(SubComite, SubComiteAdmin)
admin.site.register(Operador, OperadorAdmin)