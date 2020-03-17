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
    path('procesar_archivos/<int:archivo_id>', views.procesar_archivos, name='procesar_archivos'),
    #Carga de datos
    #Vehiculos
    path('listar_vehiculos', views.listar_vehiculos, name='listar_vehiculos'),
    path('ver_vehiculo/<int:vehiculo_id>', views.ver_vehiculo, name='ver_vehiculo'),
    path('cargar_vehiculo', views.cargar_vehiculo, name='cargar_vehiculo'),
    #Individuos
    path('listar_individuos', views.listar_individuos, name='listar_individuos'),
    path('cargar_pasajero/<int:vehiculo_id>', views.cargar_individuo, name='cargar_pasajero'),
    path('ver_individuo/<int:individuo_id>', views.ver_individuo, name='ver_individuo'),
    path('cargar/individuo', views.cargar_individuo, name='cargar_individuo'),
    path('mod/individuo/<int:individuo_id>', views.cargar_individuo, name='mod_individuo'),
    path('cargar/domicilio/<int:individuo_id>', views.cargar_domicilio, name='cargar_domicilio'),
    path('cargar/evento/<int:individuo_id>', views.cargar_evento, name='cargar_evento'),
    path('cargar/sintoma/<int:individuo_id>', views.cargar_sintoma, name='cargar_sintoma'),
]