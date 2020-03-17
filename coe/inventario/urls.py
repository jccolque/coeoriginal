#imports django
from django.urls import path
#Import de modulos personales
from . import views

app_name = 'inventario'
urlpatterns = [
    path('', views.menu, name='menu'),
    #Basico Items
    path('listar', views.lista_items, name='lista_items'),
    path('listar/rubro/<int:rubro_id>', views.lista_items, name='lista_rubro'),
    path('listar/subgrupo/<int:subgrupo_id>', views.lista_items, name='lista_subgrupo'),
    path('ver/<int:item_id>', views.ver_item, name='ver_item'),
    path('crear', views.crear_item, name='crear_item'),
    path('mod/<int:item_id>', views.crear_item, name='mod_item'),
    #eventos:
    path('crear/evento/<int:item_id>', views.crear_evento, name='crear_evento'),
    path('devolver/<int:evento_id>', views.devolver_item, name='devolver'),
]