#imports django
from django.urls import path
#Import de modulos personales
from . import apis as info_apis

#Definimos paths de la app
app_name = 'apis'
urlpatterns = [
    path('registro', info_apis.registro_covidapp, name='registro_covidapp'),
    path('encuesta', info_apis.encuesta_covidapp, name='encuesta_covidapp'),
    path('temperatura', info_apis.temperatura_covidapp, name='temperatura_covidapp'),
]