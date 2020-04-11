#imports django
from django.urls import path
#Import de modulos personales
from . import geo_views as geo_views

#Definimos paths de la app
app_name = 'geo_urls'
urlpatterns = [
    #App
    path('', geo_views.menu_geotracking, name='menu_geotracking'),
    #Tracking
    path('general', geo_views.control_tracking, name='control_tracking'),
    path('lista/alertas', geo_views.lista_alertas, name='lista_alertas'),
    path('lista/procesadas', geo_views.alertas_procesadas, name='alertas_procesadas'),
    path('ver/<int:individuo_id>', geo_views.ver_tracking, name='ver_tracking'),
    path('procesar/<int:geoposicion_id>', geo_views.procesar_alerta, name='procesar_alerta'),
]