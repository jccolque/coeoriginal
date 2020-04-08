#Imports Standard de Django
from django.contrib import admin
#Import de la app
from .models import Noticia

# Register your models here.
class NoticiaAdmin(admin.ModelAdmin):
    list_filter = ['destacada']

#Los mandamos al admin
admin.site.register(Noticia, NoticiaAdmin)