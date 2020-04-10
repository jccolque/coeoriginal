#imports django
from django.urls import path
#Import de modulos personales
from . import ws_apis as ws_apis

#Definimos paths de la app
app_name = 'ws_urls'
urlpatterns = [
    #WebServices
    path('situaciones', ws_apis.ws_situaciones, name='ws_situaciones'),

    #Choices    
    path('tipo_estado', ws_apis.tipo_estado, name='tipo_estado'),
    path('tipo_conducta', ws_apis.tipo_conducta, name='tipo_conducta'),
    path('tipo_permiso', ws_apis.tipo_permiso, name='tipo_permiso'),
]