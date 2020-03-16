#imports django
from django.urls import path
#Import de modulos personales
from . import views

app_name = 'inventario'
urlpatterns = [
    path('', views.menu, name='menu'),
]