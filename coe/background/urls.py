#Imports Django
from django.conf.urls import url
from django.urls import path
#Imports de la app
from . import views

#Definimos nuestros paths
app_name = 'background'
urlpatterns = [
    path('', views.lista_background, name='lista_background'),
    path('progreso/id/<int:task_id>', views.ver_background, name='ver_background'),
    path('progreso/name/<str:task_name>', views.ver_background, name='ver_background'),
    #Detener tarea
    #pausar tarea
]