#Imports Standard de Django
from django.contrib import admin
#Import de la app
from .models import Noticia, Parte

# Register your models here.
class NoticiaAdmin(admin.ModelAdmin):
    list_filter = ['destacada']

class ParteAdmin(admin.ModelAdmin):
    list_filter = ['destacada']

#Los mandamos al admin
admin.site.register(Noticia, NoticiaAdmin)
admin.site.register(Parte, ParteAdmin)