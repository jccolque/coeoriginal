#imports django
from django.urls import path
#Import de modulos personales
from . import app_apis as app_apis
from . import ws_apis as ws_apis

#Definimos paths de la app
app_name = 'api_urls'
urlpatterns = [
    #App
    path('config', app_apis.AppConfig, name='AppConfig'),
    path('registro', app_apis.registro, name='registro'),
    path('foto_perfil', app_apis.foto_perfil, name='foto_perfil'),
    path('encuesta', app_apis.encuesta, name='encuesta'),
    path('temperatura', app_apis.temperatura, name='temperatura'),
    path('start/tracking', app_apis.start_tracking, name='start_tracking'),
    path('tracking', app_apis.tracking, name='tracking'),
    path('salvoconducto', app_apis.salvoconducto, name='salvoconducto'),
    #WebServices
    path('situaciones', ws_apis.ws_situaciones, name='ws_situaciones'),

    #Parametros:
    path('tipo_permisos', app_apis.tipo_permisos, name='tipo_permisos'),
]