#imports django
from django.urls import path
#Import de modulos personales
from . import views

#Definimos paths de la app
app_name = 'informacion'
urlpatterns = [
    path('', views.menu, name='menu'),
    #Archivos
    path('archivos_pendientes/', views.archivos_pendientes, name='archivos_pendientes'),
    path('ver_archivo/<int:archivo_id>', views.ver_archivo, name='ver_archivo'),
    path('subir_archivos', views.subir_archivos, name='subir_archivos'),
    #Carga de datos
]