#imports django
from django.urls import path
#imports extra
#Import de modulos personales
from . import views

#Definimos los paths de la app
app_name = 'denuncias'
urlpatterns = [
    path('', views.menu, name='menu'),
    #Basico Items
    path('lista', views.lista_denuncias, name='lista_denuncias'),
    path('lista/tipo/<str:tipo>', views.lista_denuncias, name='lista_filtro_tipo'),
    path('lista/estado/<str:estado>', views.lista_denuncias, name='lista_filtro_estado'),
    #Ver denuncias
    path('ver/<int:denuncia_id>', views.ver_denuncia, name='ver_denuncia'),
    #administrar:
    path('evolucionar/<int:denuncia_id>', views.evolucionar_denuncia, name='evolucionar_denuncia'),
    path('eliminar/<int:denuncia_id>', views.eliminar_denuncia, name='eliminar_denuncia'),
]