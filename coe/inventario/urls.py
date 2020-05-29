#imports django
from django.conf.urls import url
from django.urls import path
#imports extra
from dal import autocomplete
#Import de modulos personales
from . import views
from . import autocomplete

#Definimos los paths de la app
app_name = 'inventario'
urlpatterns = [
    path('', views.menu, name='menu'),
    #Rubro:
    path('crear/rubro', views.crear_rubro, name='crear_rubro'),
    path('mod/rubro/<int:rubro_id>', views.crear_rubro, name='mod_rubro'),
    #Subgrupo:
    path('crear/subgrupo', views.crear_subgrupo, name='crear_subgrupo'),
    path('crear/subgrupo/<int:subgrupo_id>', views.crear_subgrupo, name='mod_subgrupo'),
    #Basico Items
    path('general', views.lista_general, name='lista_general'),
    path('detallada', views.lista_detallada, name='lista_detallada'),
    path('rubro/<int:rubro_id>', views.lista_detallada, name='lista_rubro'),
    path('subgrupo/<int:subgrupo_id>', views.lista_detallada, name='lista_subgrupo'),
    path('ver/<int:item_id>', views.ver_item, name='ver_item'),
    path('crear', views.crear_item, name='crear_item'),
    path('mod/<int:item_id>', views.crear_item, name='mod_item'),
    path('cargar/geoposicion/<int:item_id>', views.cargar_geoposicion, name='cargar_geoposicion'),
    #eventos:
    path('crear/evento/<int:item_id>', views.crear_evento, name='crear_evento'),
    path('devolver/<int:evento_id>', views.devolver_item, name='devolver'),
    path('transferir/<int:item_id>', views.transferir_item, name='transferir_item'),
    #Reportes
    path('csv/', views.csv_inventario, name='csv_inventario'),
    #Autocomplete
    url(r'^rubros-autocomplete/$', autocomplete.RubrosAutocomplete.as_view(), name='rubros-autocomplete',),
    url(r'^subgrupos-autocomplete/$', autocomplete.SubgruposAutocomplete.as_view(), name='subgrupos-autocomplete',),
    url(r'^items-autocomplete/$', autocomplete.ItemsAutocomplete.as_view(), name='items-autocomplete',),
]