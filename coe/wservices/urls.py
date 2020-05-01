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
    path('aislados', views.ws_aislados, name='ws_aislados'),
    #Choices    
    path('tipo_estado', views.tipo_estado, name='tipo_estado'),
    path('tipo_conducta', views.tipo_conducta, name='tipo_conducta'),
    path('tipo_permiso', views.tipo_permiso, name='tipo_permiso'),
    path('tipo_denuncia', views.tipo_denuncia, name='tipo_denuncia'),
]