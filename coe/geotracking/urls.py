#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views as views
from . import autocomplete

#Definimos paths de la app
app_name = 'geotracking'
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
    #Panel GeoOperador
    path('lista/sin_geoperador', views.lista_sin_geoperador, name='lista_sin_geoperador'),
    path('asignar/geoperador/<individuo_id>', views.asignar_geoperador, name='asignar_geoperador'),
    path('lista/geooperadores', views.lista_geooperadores, name='lista_geooperadores'),
    path('agregar/geoperador', views.agregar_geoperador, name='agregar_geoperador'),
    path('del/geoperador/<geoperador_id>', views.del_geoperador, name='del_geoperador'),
    #Panel
    path('cambiar_base/<int:geoposicion_id>', views.cambiar_base, name='cambiar_base'),
    path('config/<int:individuo_id>', views.config_tracking, name='config_tracking'),
    path('panel/geooperador', views.panel_geoperador, name='panel_geoperador'),
    path('panel/geooperador/<int:geoperador_id>', views.panel_geoperador, name='ver_geopanel'),
    path('agregar/individuo/<int:geoperador_id>', views.agregar_individuo, name='agregar_individuo'),
    path('quitar/individuo/<int:geoperador_id>/<int:individuo_id>', views.quitar_individuo, name='quitar_individuo'),
    #Autocomplete
    url(r'^individuostrackeados-autocomplete/$', autocomplete.IndividuosTrackeadosAutocomplete.as_view(), name='individuostrackeados-autocomplete',),
    url(r'^geoperadores-autocomplete/$', autocomplete.GeOperadoresAutocomplete.as_view(), name='geoperadores-autocomplete',),
    #Wservice
    path('json/<str:num_doc>', views.json_individuo, name='json_individuo'),
]