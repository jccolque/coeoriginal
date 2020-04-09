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
    path('registro', app_apis.registro_covidapp, name='registro_covidapp'),
    path('encuesta', app_apis.encuesta_covidapp, name='encuesta_covidapp'),
    path('temperatura', app_apis.temperatura_covidapp, name='temperatura_covidapp'),
    path('start/tracking', app_apis.start_tracking_covidapp, name='start_tracking_covidapp'),
    path('tracking', app_apis.tracking_covidapp, name='tracking_covidapp'),
    #WebServices
    path('situaciones', ws_apis.ws_situaciones, name='ws_situaciones'),
]