#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views

app_name = 'documentos'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('cargar', views.cargar_documento, name='cargar_documento'),
    path('mod/<int:documento_id>', views.cargar_documento, name='mod_documento'),
    path('cargar/file/<int:documento_id>', views.cargar_actualizacion, name='cargar_actualizacion'),
    path('lista', views.lista_general, name='lista_general'),
    path('lista/subco/<int:subco_id>', views.lista_general, name='lista_subcomite'),
    path('ver/<int:documento_id>', views.ver_documento, name='ver_documento'),
    #Manejo docs
    path('estado/<int:documento_id>', views.cambiar_estado, name='cambiar_estado'),
    path('del/doc/<int:documento_id>', views.eliminar_doc, name='eliminar_doc'),
    path('del/ver/<int:version_id>', views.eliminar_version, name='eliminar_version'),
    #PUBLICO
    path('lista/publica', views.lista_publica, name='ver_publicos'),
]