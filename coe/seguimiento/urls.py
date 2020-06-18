#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views as views
from . import autocomplete

#Definimos paths de la app
app_name = 'seguimiento'
urlpatterns = [
    #Publico:
    path('alta', views.buscar_alta_aislamiento, name='buscar_alta_aislamiento'),
    path('test', views.pedir_test, name='pedir_test'),
    #Menu
    path('', views.menu_seguimiento, name='menu_seguimiento'),
    #Base
    path('lista/seguimientos', views.lista_seguimientos, name='lista_seguimientos'),
    path('ver/<int:individuo_id>', views.ver_seguimiento, name='ver_seguimiento'),
    #Lista Para Liberar:
    path('lista/esperando/alta', views.esperando_alta_seguimiento, name='esperando_alta_seguimiento'),
    path('dar/alta/<int:individuo_id>', views.dar_alta, name='dar_alta'),
    path('lista/altas/realizadas', views.altas_realizadas, name='altas_realizadas'),
    #Seguimiento
    path('cargar/seguimiento/<int:individuo_id>', views.cargar_seguimiento, name='cargar_seguimiento'),
    path('cargar/seguimiento/<int:individuo_id>/tipo/<str:tipo>', views.cargar_seguimiento, name='cargar_seguimiento'),
    path('mod/seguimiento/<int:individuo_id>/<int:seguimiento_id>', views.cargar_seguimiento, name='mod_seguimiento'),
    path('del/seguimiento/<int:seguimiento_id>', views.del_seguimiento, name='del_seguimiento'),
    #Administracion
    path('lista/vigias', views.lista_vigias, name='lista_vigias'),
    path('agregar/vigia', views.agregar_vigia, name='agregar_vigia'),
    path('mod/vigia/<int:vigia_id>', views.agregar_vigia, name='mod_vigia'),
    path('del/vigia/<int:vigia_id>', views.del_vigia, name='del_vigia'),
    path('lista/sin/vigias', views.lista_sin_vigias, name='lista_sin_vigias'),
    #Cazador 360
    path('operativos/situacion', views.situacion_operativos, name='situacion_operativos'),
    path('operativos/lista', views.lista_operativos, name='lista_operativos'),
    path('operativo/crear', views.crear_operativo, name='crear_operativo'),
    path('operativo/mod/<int:operativo_id>', views.crear_operativo, name='mod_operativo'),
    path('operativo/del/<int:operativo_id>', views.del_operativo, name='del_operativo'),
    path('operativo/ver/<int:operativo_id>', views.ver_operativo, name='ver_operativo'),
    path('operativo/agregar/cazador/<int:operativo_id>', views.agregar_cazador, name='agregar_cazador'),
    path('operativo/quitar/cazador/<int:operativo_id>/<int:individuo_id>', views.quitar_cazador, name='quitar_cazador'),
    path('operativo/agregar/testeado/<int:operativo_id>', views.agregar_testeado, name='agregar_testeado'),
    path('operativo/quitar/testeado/<int:operativo_id>/<int:individuo_id>', views.quitar_testeado, name='quitar_testeado'),
    path('operativo/iniciar/<int:operativo_id>', views.iniciar_operativo, name='iniciar_operativo'),
    path('operativo/finalizar/<int:operativo_id>', views.finalizar_operativo, name='finalizar_operativo'),
    
    #path('operativo/quitar/testeado/<int:operativo_id>/<int:individuo_id>', views.quitar_testeado, name='quitar_testeado'),
    #Otros Listados
    path('test/pedidos', views.ranking_test, name='ranking_test'),
    path('test/esperando', views.esperando_test, name='esperando_test'),
    path('test/realizados', views.test_realizados, name='test_realizados'),
    path('lista/sin_telefono', views.lista_sin_telefono, name='lista_sin_telefono'),
    path('lista/autodiagnosticos', views.lista_autodiagnosticos, name='lista_autodiagnosticos'),
    path('lista/aislados', views.lista_aislados, name='lista_aislados'),
    #Situacion
    path('situacion/vigilancia', views.situacion_vigilancia, name='situacion_vigilancia'),
    path('seguimientos/vigia/<int:vigia_id>', views.seguimientos_vigia, name='seguimientos_vigia'),
    #Panel
    path('panel/vigia', views.panel_vigia, name='mi_panel'),
    path('panel/vigia/<int:vigia_id>', views.panel_vigia, name='ver_panel'),
    path('agregar/vigilado/<int:vigia_id>', views.agregar_vigilado, name='agregar_vigilado'),
    path('quitar/vigilado/<int:vigia_id>/<int:individuo_id>', views.quitar_vigilado, name='quitar_vigilado'),
    #Autocomplete
    url(r'^individuosvigilados-autocomplete/$', autocomplete.IndividuosVigiladosAutocomplete.as_view(), name='individuosvigilados-autocomplete',),
    url(r'^vigias-autocomplete/$', autocomplete.VigiasAutocomplete.as_view(), name='vigias-autocomplete',),
]