#Imports de Django
from django.conf.urls import url
from django.urls import path
#Imports de la app
from . import views
#Definimos nuestros Paths
app_name = 'consultas'
urlpatterns = [
    #Publico
    path('consulta', views.contacto, name='consultas'),
    #Consultas
    path('', views.menu, name='menu'),
    path('lista/consultas', views.lista_consultas, name='lista_consultas'),
    path('lista/respondidas', views.lista_respondidas, name='lista_respondidas'),
    path('ver/consulta/<int:consulta_id>', views.ver_consulta, name='ver_consulta'),
    path('consulta/respondida/<int:consulta_id>', views.consulta_respondida, name='consulta_respondida'),

    #Validar
    url(r'^act_consulta/(?P<consulta_id>[0-9]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activar_consulta, name='activar_consulta'),
]