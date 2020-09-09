#imports django
from django.urls import path
#Import de modulos personales
from . import views as views

#Definimos paths de la app
app_name = 'wservices'
urlpatterns = [
    path('', views.menu, name='menu'),
    #Generico
    path('ws/', views.ws, name='ws'),
    path('ws/<str:nombre_app>/<str:nombre_modelo>/', views.ws, name='ws'),
    #WebServices
    path('situaciones', views.ws_situaciones, name='ws_situaciones'),
    path('localidades', views.ws_localidades, name='ws_localidades'),
    path('barrios', views.ws_barrios, name='ws_barrios'),
    path('barrios/<int:localidad_id>', views.ws_barrios, name='ws_barrios_filtrados'),
    #Informacion Especifica
    path('aislados', views.ws_aislados, name='ws_aislados'),
    path('ocupacion', views.ws_ocupacion, name='ws_ocupacion'),
    path('seguimientos', views.ws_seguimientos, name='ws_seguimientos'),
    path('atributos', views.ws_atributos, name='ws_atributos'),
    path('llamadas', views.ws_llamadas, name='ws_llamadas'),
    #Choices    
    path('tipo_estado', views.tipo_estado, name='tipo_estado'),
    path('tipo_conducta', views.tipo_conducta, name='tipo_conducta'),
    path('tipo_permiso', views.tipo_permiso, name='tipo_permiso'),
    path('tipo_denuncia', views.tipo_denuncia, name='tipo_denuncia'),
    #GIS
    path('confirmados_gis', views.ws_confirmados_gis, name='confirmados_gis'),
    path('recuperados_gis', views.ws_recuperados_gis, name='recuperados_gis'),
    path('fallecidos_gis', views.ws_fallecidos_gis, name='fallecidos_gis'),
    path('pcr_gis', views.ws_pcr_gis, name='pcr_gis'),
]