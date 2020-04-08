from django.contrib import admin
from .models import  Consulta, Respuesta
# Register your models here.
#Definimos inline:
class RespuestaInline(admin.TabularInline):
    model = Respuesta
    fk_name = 'consulta'
    extras = 0

#Definimos nuestros modelos
class ConsultaAdmin(admin.ModelAdmin):
    model = Consulta
    search_fields = ['autor', 'asunto']
    list_filter = ['valida', 'respondida', ]
    inlines = [RespuestaInline, ]

admin.site.register(Consulta, ConsultaAdmin)