#imports django
from django.urls import path
#Import de modulos personales
from . import views

app_name = 'operadores'
urlpatterns = [
    path('', views.menu, name='menu'),
    #ABM SubComites
    path('listar/subco', views.listar_subcomites, name='listar_subcomites'),
    path('ver/subco/<int:subco_id>', views.ver_subcomite, name='ver_subcomite'),
    path('crear/subco', views.crear_subcomite, name='crear_subcomite'),
    #ABM Operadores
    path('listar/op', views.listar_operadores, name='listar_operadores'),
    path('crear/op', views.crear_operador, name='crear_operador'),
    path('modificar/op/<int:operador_id>', views.mod_operador, name='modificar_usuario'),
    path('chpass/op/<int:operador_id>', views.cambiar_password, name='cambiar_password'),
    path('desactivar/op/<int:operador_id>', views.desactivar_usuario, name='desactivar_usuario'),
    path('activar/op/<int:operador_id>', views.activar_usuario, name='activar_usuario'),
    path('credencial/op/<int:operador_id>', views.ver_credencial, name='ver_credencial'),
    #Auditoria
    path('auditoria', views.auditoria, name='auditoria'),
    path('auditoria/<int:user_id>', views.auditoria, name='auditoria_propia'),
    #Asistencia
    path('presentes', views.listado_presentes, name='listado_presentes'),
    path('checkin', views.checkin, name='checkin'),
    path('ingreso/<int:operador_id>', views.ingreso, name='ingreso'),
    path('checkout/<int:operador_id>', views.checkout, name='checkout'),
    path('asistencia', views.registro_asistencia, name='registro_asistencia'),
]