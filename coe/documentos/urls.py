#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
#from . import autocomplete

app_name = 'documentos'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('cargar', views.cargar_documento, name='cargar_documento'),
    path('cargar/file/<int:documento_id>', views.cargar_actualizacion, name='cargar_actualizacion'),
    path('lista', views.lista_general, name='lista_general'),
    path('lista/subco/<int:subco_id>', views.lista_general, name='lista_detallada'),
    path('ver/<int:documento_id>', views.ver_documento, name='ver_documento'),
]