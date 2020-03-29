#Imports de django
from django.contrib import admin
#Imports Extras
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
#Imports de la app
from .models import Grafico, Columna, Dato

#Definimos los inlines:
class DatoInline(NestedStackedInline):
    model = Dato
    fk_name = 'columna'
    extra = 0

class ColumnaInline(NestedStackedInline):
    model = Columna
    fk_name = 'grafico'
    inlines = [DatoInline, ]
    extra = 1

#Definimos nuestros customadmin
class GraficoAdmin(NestedModelAdmin):
    model = Grafico
    search_fields = ['nombre', 'verbose_name', ]
    list_filter = ['tipo', ]
    inlines = [ColumnaInline, ]

# Register your models here.
admin.site.register(Grafico, GraficoAdmin)