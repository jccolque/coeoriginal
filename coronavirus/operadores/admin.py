#Imports Django
from django.contrib import admin
#Imports extras

#Imports de la app
from .models import Operador

#Definimos nuestros modelos administrables:
class OperadorAdmin(admin.ModelAdmin):
    model = Operador
    list_filter = ['organismo']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'num_doc']
    readonly_fields = ['qrpath']
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(Operador, OperadorAdmin)