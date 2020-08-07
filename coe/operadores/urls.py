#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
from . import autocomplete

app_name = 'operadores'
urlpatterns = [
    path('', views.menu, name='menu'),
    #ABM SubComites
    path('listar/subco', views.listar_subcomites, name='listar_subcomites'),
    path('ver/subco/<int:subco_id>', views.ver_subcomite, name='ver_subcomite'),
    path('crear/subco', views.crear_subcomite, name='crear_subcomite'),
    path('mod/subco/<int:subco_id>', views.crear_subcomite, name='mod_subcomite'),
    #ABM Operadores
    path('listar/op', views.listar_operadores, name='listar_operadores'),
    path('crear/op', views.crear_operador, name='crear_operador'),
    path('modificar/op/<int:operador_id>', views.mod_operador, name='modificar_usuario'),
    path('check/individuo/<int:operador_id>', views.check_individuo, name='check_individuo'),
    path('chpass/op/<int:operador_id>', views.cambiar_password, name='cambiar_password'),
    path('desactivar/op/<int:operador_id>', views.desactivar_usuario, name='desactivar_usuario'),
    path('activar/op/<int:operador_id>', views.activar_usuario, name='activar_usuario'),
    path('credencial/op/<int:operador_id>', views.ver_credencial, name='ver_credencial'),
    path('imprimir', views.imprimir_tarjetas, name='imprimir_tarjetas'),
    #Auditoria
    path('auditoria', views.auditoria, name='auditoria'),
    path('auditoria/<int:user_id>', views.auditoria, name='auditoria_propia'),
    path('auditar/obj/<int:content_id>/<int:object_id>', views.auditar_cambios, name='auditar_cambios'),
    path('asistencia/<int:operador_id>', views.asistencia, name='asistencia'),
    #Asistencia
    path('presentes', views.listado_presentes, name='listado_presentes'),
    path('checkin', views.checkin, name='checkin'),
    path('ingreso/<int:operador_id>', views.ingreso, name='ingreso'),
    path('checkout/<int:operador_id>', views.checkout, name='checkout'),
    path('asistencia', views.registro_asistencia, name='registro_asistencia'),
    #Reportes
    path('csv/', views.csv_operadores, name='csv_operadores'),
    #Autocomplete
    url(r'^operadores-autocomplete/$', autocomplete.OperadoresAutocomplete.as_view(), name='operadores-autocomplete',),
    url(r'^subcomite-autocomplete/$', autocomplete.SubComiteAutocomplete.as_view(), name='subcomite-autocomplete',),
]