#Imports de Django
from django.conf.urls import url
from django.urls import path
#Imports de la app
from . import views
#Definimos nuestros Paths
app_name = 'consultas'
urlpatterns = [
    #Publico
    path('consulta', views.contacto, name='consultas'),
    #Consultas
    path('', views.menu, name='menu'),
    path('lista/consultas', views.lista_consultas, name='lista_consultas'),
    path('lista/respondidas', views.lista_respondidas, name='lista_respondidas'),
    path('ver/consulta/<int:consulta_id>', views.ver_consulta, name='ver_consulta'),
    path('consulta/respondida/<int:consulta_id>', views.consulta_respondida, name='consulta_respondida'),
    #Denuncias
    path('denuncias/lista', views.lista_denuncias, name='lista_denuncias'),
    path('denuncias/lista/tipo/<str:tipo>', views.lista_denuncias, name='lista_filtro_tipo'),
    path('denuncias/lista/estado/<str:estado>', views.lista_denuncias, name='lista_filtro_estado'),
    path('denuncia/ver/<int:denuncia_id>', views.ver_denuncia, name='ver_denuncia'),
    path('denuncias/evolucionar/<int:denuncia_id>', views.evolucionar_denuncia, name='evolucionar_denuncia'),
    path('denuncias/eliminar/<int:denuncia_id>', views.eliminar_denuncia, name='eliminar_denuncia'),
    #Telefonistas
    #Administrar
    path('informe_actividad', views.informe_actividad, name='informe_actividad'),
    path('lista/telefonistas', views.lista_telefonistas, name='lista_telefonistas'),
    path('telefonista/agregar', views.agregar_telefonista, name='agregar_telefonista'),
    path('telefonista/mod/<int:telefonista_id>', views.agregar_telefonista, name='mod_telefonista'),
    path('telefonista/del/<int:telefonista_id>', views.del_telefonista, name='del_telefonista'),
    
    path('lista/llamadas', views.lista_llamadas, name='lista_llamadas'),
    path('lista/llamadas/tel/<int:telefonista_id>', views.lista_llamadas, name='llamadas_telefonista'),
    path('lista/consultas/tel/<int:telefonista_id>', views.lista_consultas, name='consultas_telefonista'),
    path('lista/denuncias/tel/<int:telefonista_id>', views.lista_denuncias, name='denuncias_telefonista'),

    path('telefonista/panel/<int:telefonista_id>', views.ver_panel, name='ver_panel'),
    path('llamada/del/<int:llamada_id>', views.del_llamada, name='del_llamada'),
    path('telefonista/actividad/<int:telefonista_id>', views.informe_actividad, name='actividad_telefonista'),

    #Trabajo
    path('telefonista/mipanel', views.ver_panel, name='mi_panel'),
    path('llamada/cargar/<int:telefonista_id>', views.cargar_llamada, name='cargar_llamada'),
    path('llamada/cargar/<int:telefonista_id>/consulta/<int:consulta_id>', views.cargar_llamada, name='cargar_llamada_consulta'),
    path('llamada/mod/<int:llamada_id>', views.cargar_llamada, name='mod_llamada'),
    #Validar
    url(r'^act_consulta/(?P<consulta_id>[0-9]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activar_consulta, name='activar_consulta'),
]