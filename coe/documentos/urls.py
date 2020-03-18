#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
#from . import autocomplete

app_name = 'documentos'
urlpatterns = [
    path('', views.menu, name='menu'),

    path('lista', views.lista_general, name='lista_general'),
    path('lista/subco/<int:subco_id>', views.lista_general, name='lista_detallada'),

    path('cargar', views.cargar_documento, name='cargar_documento'),

]