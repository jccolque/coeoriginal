#imports django
from django.urls import path
#Import de modulos personales
from . import views as views

#Definimos paths de la app
app_name = 'geo_urls'
urlpatterns = [
    #App
    path('', views.menu_geotracking, name='menu_geotracking'),
    #Tracking
    path('general', views.control_tracking, name='control_tracking'),
    path('lista/trackeados', views.lista_trackeados, name='lista_trackeados'),
    path('lista/alertas', views.lista_alertas, name='lista_alertas'),
    path('lista/procesadas', views.alertas_procesadas, name='alertas_procesadas'),
    path('ver/<int:individuo_id>', views.ver_tracking, name='ver_tracking'),
    path('procesar/<int:geoposicion_id>', views.procesar_alerta, name='procesar_alerta'),
    #Admin
    path('cambiar_base/<int:geoposicion_id>', views.cambiar_base, name='cambiar_base'),
    path('config/<int:individuo_id>', views.config_tracking, name='config_tracking'),
]