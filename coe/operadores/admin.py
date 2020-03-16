#Imports Django
from django.contrib import admin
#Imports extras

#Imports de proyecto
from core.admin import register_hidden_models
#Imports de la app
from .models import SubComite, Operador

#Definimos nuestros modelos administrables:
class OperadorAdmin(admin.ModelAdmin):
    model = Operador
    list_filter = ['organismo']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'num_doc']
    readonly_fields = ['qrpath']
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
register_hidden_models(SubComite)
admin.site.register(Operador, OperadorAdmin)