#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views

#Definimos paths de la app
app_name = 'graficos'
urlpatterns = [
    #Administrador
    path('', views.menu, name='menu'),
    #Listados
    path('lista', views.lista_graficos, name='lista_graficos'),
    path('lista/tipo/<str:tipo_id>', views.lista_graficos, name='lista_tipo'),
    path('ver/<int:grafico_id>', views.ver_grafico, name='ver_grafico'),
    #ABM GRAFICO
    path('crear', views.crear_grafico, name='crear_grafico'),
    path('mod/<int:grafico_id>', views.crear_grafico, name='mod_grafico'),
    path('reset/<int:grafico_id>', views.reniciar_datos, name='reniciar_datos'),
    path('cambiar/estado/<int:grafico_id>', views.cambiar_estado, name='cambiar_estado'),
    #ABM DATOS
    path('crear/columna/<int:grafico_id>', views.crear_columna, name='crear_columna'),
    path('mod/columna/<int:grafico_id>/<int:columna_id>', views.crear_columna, name='mod_columna'),
    
    path('crear/dato/<int:grafico_id>', views.crear_dato, name='crear_dato'),
    path('mod/dato/<int:grafico_id>/<int:dato_id>', views.crear_dato, name='mod_dato'),

]