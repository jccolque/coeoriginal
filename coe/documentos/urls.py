#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
#from . import autocomplete

app_name = 'documentos'
urlpatterns = [
    path('', views.menu, name='menu'),
]