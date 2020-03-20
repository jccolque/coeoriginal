#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
from . import autocomplete

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
    path('buscar/vehiculo/', views.buscar_vehiculo, name='buscar_vehiculo'),
    path('listar_vehiculos', views.listar_vehiculos, name='listar_vehiculos'),
    path('vehiculos/tipo/<int:tipo_id>', views.listar_vehiculos, name='vehiculos_tipo'),
    path('ver_vehiculo/<int:vehiculo_id>', views.ver_vehiculo, name='ver_vehiculo'),
    path('cargar_vehiculo', views.cargar_vehiculo, name='cargar_vehiculo'),
    #Individuos
    path('buscar/individuo/', views.buscar_individuo, name='buscar_individuo'),
    path('listar/individuos', views.lista_individuos, name='listar_individuos'),
    path('listar/seguimiento', views.lista_seguimiento, name='lista_seguimiento'),
    path('cargar_pasajero/<int:vehiculo_id>', views.cargar_individuo, name='cargar_pasajero'),
    path('ver_individuo/<int:individuo_id>', views.ver_individuo, name='ver_individuo'),
    path('cargar/individuo', views.cargar_individuo, name='cargar_individuo'),
    path('mod/individuo/<int:individuo_id>', views.cargar_individuo, name='mod_individuo'),
    path('cargar/domicilio/<int:individuo_id>', views.cargar_domicilio, name='cargar_domicilio'),
    path('cargar/seguimiento/<int:individuo_id>', views.cargar_seguimiento, name='cargar_seguimiento'),
    path('cargar/situacion/<int:individuo_id>', views.cargar_situacion, name='cargar_situacion'),
    path('cargar/relacion/<int:individuo_id>', views.cargar_relacion, name='cargar_relacion'),
    path('cargar/atributo/<int:individuo_id>', views.cargar_atributo, name='cargar_atributo'),
    path('cargar/sintoma/<int:individuo_id>', views.cargar_sintoma, name='cargar_sintoma'),
    path('cargar/geopos/<int:domicilio_id>', views.cargar_geoposicion, name='cargar_geoposicion'),

    #Reportes
    path('reporte/basico', views.reporte_basico, name='reporte_basico'),
    path('csv/individuos/', views.csv_individuos, name='csv_individuos'),
    #Autocomplete
    url(r'^sintomas-autocomplete/$', autocomplete.SintomaAutocomplete.as_view(), name='sintomas-autocomplete',),
    url(r'^atributos-autocomplete/$', autocomplete.AtributoAutocomplete.as_view(), name='atributos-autocomplete',),
    url(r'^individuos-autocomplete/$', autocomplete.IndividuosAutocomplete.as_view(), name='individuos-autocomplete',),
]