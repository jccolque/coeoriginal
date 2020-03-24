#Imports de Django
from django.conf.urls import url
from django.urls import path
#Imports de la app
from . import views
from . import autocomplete
#Definimos nuestros Paths
app_name = 'core'
urlpatterns = [
    #Home
    url(r'^$', views.home, name='home'),
    path('faqs', views.faqs, name='faqs'),
    path('contacto', views.contacto, name='contacto'),

    #Administracion
    path('core', views.menu, name='menu'),
    path('lista/consultas', views.lista_consultas, name='lista_consultas'),
    path('ver/consulta/<int:consulta_id>', views.ver_consulta, name='ver_consulta'),
    path('consulta/respondida/<int:consulta_id>', views.consulta_respondida, name='consulta_respondida'), 
    #Acceso de usuarios
    path('login', views.home_login, name='home_login'),
    path('logout', views.home_logout, name='home_logout'),

    #Validaciones:
    url(r'^act_usuario/(?P<usuario_id>[0-9]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activar_usuario_mail, name='activar_usuario_mail'),
    url(r'^act_consulta/(?P<consulta_id>[0-9]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activar_consulta, name='activar_consulta'),
    #Autocomplete
    url(r'^usuarios-autocomplete/$', autocomplete.UsuariosAutocomplete.as_view(), name='usuarios-autocomplete',),
    url(r'^organismos-autocomplete/$', autocomplete.OrganismosAutocomplete.as_view(), name='organismos-autocomplete',),
    #Web Services
    path('ws/', views.ws, name='ws'),
    path('ws/<str:nombre_app>/<str:nombre_modelo>/', views.ws, name='ws'),
]