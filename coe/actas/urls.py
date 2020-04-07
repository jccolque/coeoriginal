#imports django
from django.urls import path
#Import de modulos personales
from . import views

app_name = 'actas'
urlpatterns = [
    path('', views.menu, name='menu'),
    path('lista', views.listar_actas, name='listar_actas'),
    path('ver/<int:acta_id>', views.ver_acta, name='ver_acta'),
    path('crear', views.crear_acta, name='crear_acta'),
    path('mod/<int:acta_id>', views.crear_acta, name='modificar_acta'),
]