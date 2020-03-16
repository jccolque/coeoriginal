#imports django
from django.urls import path
#Import de modulos personales
from . import views

app_name = 'operadores'
urlpatterns = [
    path('', views.menu, name='menu'),
    #ABM Operadores
    path('listar', views.listar_operadores, name='listar_operadores'),
    path('crear', views.crear_operador, name='crear_operador'),
    path('modificar/<int:operador_id>', views.crear_operador, name='modificar_usuario'),
    path('chpass/<int:operador_id>', views.cambiar_password, name='cambiar_password'),
    path('desactivar/<int:operador_id>', views.desactivar_usuario, name='desactivar_usuario'),
    path('activar/<int:operador_id>', views.activar_usuario, name='activar_usuario'),
    path('credencial/<int:operador_id>', views.ver_credencial, name='ver_credencial'),

    #Asistencia
    path('presentes', views.listado_presentes, name='listado_presentes'),
    path('checkin', views.checkin, name='checkin'),
    path('checkout/<int:operador_id>', views.checkout, name='checkout'),
    path('asistencia', views.registro_asistencia, name='registro_asistencia'),
]