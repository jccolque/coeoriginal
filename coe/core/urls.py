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
    path('consejos', views.consejos, name='consejos'),
    path('entregas', views.entregas, name='entregas'),
    #Administracion
    path('core', views.menu, name='menu'),

    #Acceso de usuarios
    path('login', views.home_login, name='home_login'),
    path('logout', views.home_logout, name='home_logout'),

    #Validaciones:
    url(r'^act_usuario/(?P<usuario_id>[0-9]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activar_usuario_mail, name='activar_usuario_mail'),
    #Autocomplete
    url(r'^usuarios-autocomplete/$', autocomplete.UsuariosAutocomplete.as_view(), name='usuarios-autocomplete',),
]