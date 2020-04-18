#imports django
from django.urls import path
#Import de modulos personales
from . import ide_apis as ide_apis

#Definimos paths de la app
app_name = 'ide_urls'
urlpatterns = [
    #App
    path('config', ide_apis.IdeConfig, name='IdeConfig'),
    path('mapeo_general', ide_apis.mapeo_general, name='mapeo_general'),
    path('tracking/<int:individuo_id>', ide_apis.tracking_individuo, name='tracking_individuo'),
]