#Imports de python
import json
import requests
#Imports django
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#Imports de la app
from .apps import CoreConfig


#Funciones para asignar a las app.configs    
def agregar_menu(app):
    CoreConfig.ADMIN_MENU += [(app.name.capitalize() , app.name)]

def paginador(request, queryset):
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 50)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)