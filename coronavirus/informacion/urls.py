#imports django
from django.urls import path
#Import de modulos personales
from . import views

#Definimos paths de la app
app_name = 'informacion'
urlpatterns = [
    path('', views.menu, name='menu'),
]