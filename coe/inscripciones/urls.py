#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
#from . import autocomplete

#Definimos paths de la app
app_name = 'inscripciones'
urlpatterns = [
    path('', views.menu, name='menu'),
]