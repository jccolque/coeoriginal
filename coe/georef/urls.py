#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
from . import autocomplete

#Definimos nuestros paths
app_name = 'georef'
urlpatterns = [
    path('', views.menu, name='menu'),
    #Administracion
    #Nacionalidad
    path('nacionalidades', views.lista_nacionalidades, name='lista_nacionalidades'),
    path('nacionalidad/crear', views.crear_nacionalidad, name='crear_nacionalidad'),
    path('nacionalidad/mod/<int:nacionalidad_id>', views.crear_nacionalidad, name='mod_nacionalidad'),
    path('nacionalidad/del/<int:nacionalidad_id>', views.delete_nacionalidad, name='delete_nacionalidad'),

    path('provincias', views.lista_provincias, name='lista_provincias'),
    path('provincia/crear', views.crear_provincia, name='crear_provincia'),
    path('provincia/mod/<int:provincia_id>', views.crear_provincia, name='mod_provincia'),
    path('provincia/del/<int:provincia_id>', views.delete_provincia, name='delete_provincia'),

    path('departamentos', views.lista_departamentos, name='lista_departamentos'),
    path('departamento/crear', views.crear_departamento, name='crear_departamento'),
    path('departamento/mod/<int:departamento_id>', views.crear_departamento, name='mod_departamento'),
    path('departamento/del/<int:departamento_id>', views.delete_departamento, name='delete_departamento'),

    path('localidades', views.lista_localidades, name='lista_localidades'),
    path('localidad/crear', views.crear_localidad, name='crear_localidad'),
    path('localidad/mod/<int:localidad_id>', views.crear_localidad, name='mod_localidad'),
    path('localidad/del/<int:localidad_id>', views.delete_localidad, name='delete_localidad'),    
    
    path('barrios', views.lista_barrios, name='lista_barrios'),
    path('barrio/crear', views.crear_barrio, name='crear_barrio'),
    path('barrio/mod/<int:barrio_id>', views.crear_barrio, name='mod_barrio'),
    path('barrio/del/<int:barrio_id>', views.delete_barrio, name='delete_barrio'),      
    
    path('ubicaciones', views.lista_ubicaciones, name='lista_ubicaciones'),
    path('ubicacion/crear', views.crear_ubicacion, name='crear_ubicacion'),
    path('ubicacion/mod/<int:ubicacion_id>', views.crear_ubicacion, name='mod_ubicacion'),
    path('ubicacion/del/<int:ubicacion_id>', views.delete_ubicacion, name='delete_ubicacion'),
    path('ubicacion/geopos/<int:ubicacion_id>', views.geopos_ubicacion, name='geopos_ubicacion'),
    #Upload
    path('upload', views.upload_localidades, name='upload_localidades'),
    #Autocompleteviews
    url(r'^nacionalidad-autocomplete/$', autocomplete.NacionalidadAutocomplete.as_view(), name='nacionalidad-autocomplete',),
    url(r'^provincia-autocomplete/$', autocomplete.ProvinciaAutocomplete.as_view(), name='provincia-autocomplete',),
    url(r'^departamento-autocomplete/$', autocomplete.DepartamentoAutocomplete.as_view(), name='departamento-autocomplete',),
    url(r'^localidad-autocomplete/$', autocomplete.LocalidadAutocomplete.as_view(), name='localidad-autocomplete',),
    url(r'^barrio-autocomplete/$', autocomplete.BarrioAutocomplete.as_view(), name='barrio-autocomplete',),
    
]