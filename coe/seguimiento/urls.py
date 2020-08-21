#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views as views
from . import autocomplete
from .views import GisDel

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
    #Seguimiento
    path('cargar/seguimiento/<int:individuo_id>', views.cargar_seguimiento, name='cargar_seguimiento'),
    path('cargar/seguimiento/<int:individuo_id>/tipo/<str:tipo>', views.cargar_seguimiento, name='cargar_seguimiento'),
    path('mod/seguimiento/<int:individuo_id>/<int:seguimiento_id>', views.cargar_seguimiento, name='mod_seguimiento'),
    path('del/seguimiento/<int:seguimiento_id>', views.del_seguimiento, name='del_seguimiento'),
    path('fin/seguimiento/<int:vigia_id>/<int:individuo_id>', views.fin_seguimiento, name='fin_seguimiento'),
    #Condicion
    path('cargar/condicion/<int:individuo_id>', views.crear_condicion, name='crear_condicion'),
    path('mod/condicion/<int:individuo_id>/<int:condicion_id>', views.crear_condicion, name='mod_condicion'),
    path('del/condicion/<int:condicion_id>', views.del_condicion, name='del_condicion'),
    path('lista/requieren/atencion', views.lista_requiere_atencion, name='lista_requiere_atencion'),
    path('lista/requieren/atencion/atrib/<str:atrib>', views.lista_requiere_atencion, name='lista_requiere_atencion_filtro'),
    path('atender/condiciones/<int:condicion_id>', views.atender_condiciones, name='atender_condiciones'),
    path('lista/atendidos', views.lista_atendidos, name='lista_atendidos'),
    #Lista Para Liberar:
    path('lista/esperando/alta', views.esperando_alta_seguimiento, name='esperando_alta_seguimiento'),
    path('dar/alta/<int:individuo_id>', views.dar_alta, name='dar_alta'),
    path('lista/altas/realizadas', views.altas_realizadas, name='altas_realizadas'),
    #Administracion
    path('lista/vigias', views.lista_vigias, name='lista_vigias'),
    path('lista/ocupacion', views.lista_ocupacion, name='lista_ocupacion'),
    path('agregar/vigia', views.agregar_vigia, name='agregar_vigia'),
    path('mod/vigia/<int:vigia_id>', views.agregar_vigia, name='mod_vigia'),
    path('del/vigia/<int:vigia_id>', views.del_vigia, name='del_vigia'),
    path('lista/sin/vigias', views.lista_sin_vigias, name='lista_sin_vigias'),
    path('vigia/mod/estado/<int:vigia_id>', views.mod_estado_vigia, name='mod_estado_vigia'),
    path('vigia/rellenar/<int:vigia_id>', views.rellenar_vigia, name='rellenar_vigia'),
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
    path('quitar/sintel/<int:individuo_id>', views.quitar_lista_sintel, name='quitar_lista_sintel'),
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
    #Gis
    path('gis/lista', views.gis_list, name="gis_list"),
    path('gis/cargar', views.cargar_gis, name="cargar_gis"),
    path('gis/mod/datos/<int:datosgis_id>', views.cargar_gis, name="mod_gis"),
    path('gis/delete/datos/<int:pk>', GisDel.as_view(), name='gis_del'),
    #Seguimiento PLP
    path('muestras/bioq/list', views.muestra_list_bioq, name="muestra_list_bioq"),
    path('muestras/comp/list', views.muestra_list_comp, name="muestra_list_comp"),
    path('muestras/panel/list', views.muestra_list_panel, name="muestra_list_panel"),
    path('muestras/edit/bioq/<int:muestra_id>', views.edit_bioq, name="edit_bioq"),
    path('muestras/buscar/persona', views.buscar_persona_muestra, name="buscar_persona_muestra"),
    path('muestras/existe/<int:individuo_id>/<str:num_doc>/', views.cargar_plp, name='existe_plp'),
    path('muestras/cargar/<str:num_doc>/', views.cargar_plp, name='cargar_plp'),
    path('muestras/editar/panel/<int:muestra_id>', views.editar_muestra, name="editar_muestra"),
    path('muestras/editar/panel/<int:muestra_id>', views.cargar_plp, name="editar_plp"),
    path('muestras/panel_editar/<int:muestra_id>', views.edit_panel, name="editar_panel_plp"),
    path('muestras/upload/masivo', views.upload_muestra, name="upload_muestra"),
    path('muestras/delete/datos/<int:pk>', views.MuestraDel.as_view(), name='muestra_del'),
    #Autocomplete
    url(r'^individuosvigilados-autocomplete/$', autocomplete.IndividuosVigiladosAutocomplete.as_view(), name='individuosvigilados-autocomplete',),
    url(r'^vigias-autocomplete/$', autocomplete.VigiasAutocomplete.as_view(), name='vigias-autocomplete',),
]