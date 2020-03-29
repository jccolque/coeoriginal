from django.contrib import admin
#Imports de la app
from .models import Grafico, Dato

#Definimos los inlines:
#class DatoInline(admin.TabularInline):
#    model = Dato
#    fk_name = 'grafico'
#    extra = 0

#Definimos nuestros customadmin
class GraficoAdmin(admin.ModelAdmin):
    model = Grafico
    search_fields = ['nombre', 'verbose_name', ]
    list_filter = ['tipo', ]
    #inlines = [DatoInline, ]


# Register your models here.
admin.site.register(Grafico, GraficoAdmin)