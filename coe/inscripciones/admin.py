#Imports Django
from django.contrib import admin
#Imports de la app
from .models import Area, Tarea, Inscripto

#Inline
class TareaInline(admin.TabularInline):
    model = Tarea
    fk_name = 'area'

#Definimos nuestros modelos administrables:
class AreaAdmin(admin.ModelAdmin):
    model = Area
    search_fields = ['nombre', ]
    inlines = [TareaInline]

class InscriptoAdmin(admin.ModelAdmin):
    model = Inscripto
    search_fields = ['num_doc', 'apellidos', 'nombres',]
    list_filter = ['profesion', 'valido', 'disponible']

# Register your models here.
admin.site.register(Area, AreaAdmin)
admin.site.register(Inscripto, InscriptoAdmin)