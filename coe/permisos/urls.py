#imports django
from django.urls import path
#Import de modulos personales
from . import views as views

#Definimos paths de la app
app_name = 'permisos'
urlpatterns = [
    #Publico
    #Permiso Online
    path('buscar/', views.buscar_permiso_web, name='buscar_permiso'),
    path('<int:individuo_id>/<int:num_doc>/', views.pedir_permiso_web, name='pedir_permiso'),
    path('datos/<int:individuo_id>', views.completar_datos, name='completar_datos'),
    path('foto/<int:individuo_id>', views.subir_foto, name='subir_foto'),
    #Ingreso Provincial
    path('ingreso/', views.pedir_ingreso_provincial, name='pedir_ingreso_provincial'),
    path('mod/ingreso/<int:ingreso_id>', views.pedir_ingreso_provincial, name='mod_ingreso_provincial'),
    path('ingreso/<str:token>', views.ver_ingreso_provincial, name='ver_ingreso_provincial'),
    path('cargar/ingresantes/<int:ingreso_id>', views.cargar_ingresante, name='cargar_ingresantes'),
    path('finalizar/ingreso/<int:ingreso_id>', views.finalizar_ingreso, name='finalizar_ingreso'),
    path('mod/ingresantes/<int:ingreso_id>/<int:individuo_id>', views.cargar_ingresante, name='mod_ingresantes'),
    path('ingreso/subir/permiso_nac/<str:token>', views.ingreso_subir_permiso_nac, name='ingreso_subir_permiso_nac'),
    path('cargar/dut/<int:ingreso_id>', views.cargar_dut, name='cargar_dut'),
    path('cargar/plan_vuelo/<int:ingreso_id>', views.cargar_plan_vuelo, name='cargar_plan_vuelo'),
    path('del/ingresante/<int:ingreso_id>/<int:individuo_id>', views.quitar_ingresante, name='quitar_ingresante'),
    path('ingreso/aprobado/<str:token>', views.ver_ingreso_aprobado, name='ver_ingreso_aprobado'),
    #Circulacion
    path('circulacion/', views.pedir_circulacion_temporal, name='pedir_circulacion_temporal'),
    path('circulacion/<int:circulacion_id>', views.pedir_circulacion_temporal, name='mod_circulacion_temporal'),
    path('circulacion/<str:token>', views.ver_circulacion_temporal, name='ver_circulacion_temporal'),
    path('circ/subir/permiso_nac/<str:token>', views.circ_subir_permiso_nac, name='circ_subir_permiso_nac'),
    path('circ/subir/licencia/<str:token>', views.circ_subir_licencia, name='circ_subir_licencia'),
    path('circ/cargar/chofer/<str:token>', views.circ_cargar_chofer, name='circ_cargar_chofer'),
    path('circ/cargar/chofer/<str:token>/<int:individuo_id>', views.circ_cargar_chofer, name='circ_mod_chofer'),
    path('circ/cargar/acomp/<str:token>', views.circ_cargar_acomp, name='circ_cargar_acomp'),
    path('circ/cargar/acomp/<str:token>/<int:individuo_id>', views.circ_cargar_acomp, name='circ_mod_acomp'),
    path('circ/comprobante/<str:token>', views.ver_comprobante_circulacion, name='ver_comprobante_circulacion'),
    path('circ/finalizar/<str:token>', views.finalizar_circulacion, name='finalizar_circulacion'),
    path('circ/del/chofer/<str:token>', views.circ_del_chofer, name='circ_del_chofer'),
    path('circ/del/acomp/<str:token>', views.circ_del_acomp, name='circ_del_acomp'),
    #  Administracion
    #Permisos
    path('', views.menu_permisos, name='menu_permisos'),
    #Niveles de Restriccion
    path('nivel/restricciones', views.situacion_restricciones, name='situacion_restricciones'),
    path('crear/nivel', views.crear_nivelrestriccion, name='crear_nivelrestriccion'),
    path('mod/nivel/<int:nivel_id>', views.crear_nivelrestriccion, name='mod_nivelrestriccion'),
    path('activar/nivel/<int:nivel_id>', views.activar_nivel, name='activar_nivel'),
    #Listados
    path('lista/activos', views.lista_activos, name='lista_activos'),
    path('lista/vencidos', views.lista_vencidos, name='lista_vencidos'),
    path('ver/permiso/<int:permiso_id>/<int:individuo_id>', views.ver_permiso, name='ver_permiso'),
    path('eliminar/permiso/<int:permiso_id>', views.eliminar_permiso, name='eliminar_permiso'),
    path('lista/nacion', views.lista_nacion, name='lista_nacion'),
    #Ingresos
    path('situacion/ingresos', views.situacion_ingresos, name='situacion_ingresos'),
    path('lista/ingresos', views.lista_ingresos, name='lista_ingresos'),
    path('lista/ingresos/estado/<str:estado>', views.lista_ingresos, name='lista_ingresos_filtro'),
    path('lista/ingresos/tipo/<str:tipo>', views.lista_ingresos, name='lista_ingresos_filtro'),
    path('ingreso/enviado/<int:ingreso_id>', views.ingreso_enviado, name='ingreso_enviado'),
    path('aprobar/ingreso/<int:ingreso_id>', views.aprobar_ingreso, name='aprobar_ingreso'),
    path('del/ingreso/<int:ingreso_id>', views.eliminar_ingreso, name='eliminar_ingreso'),
    path('email/ingreso/<int:ingreso_id>', views.ingreso_enviar_email, name='ingreso_enviar_email'),
    #Circulacion Temporal
    path('lista/circulaciones', views.lista_circulaciones, name='lista_circulaciones'),
    path('lista/circulaciones/estado/<str:estado>', views.lista_circulaciones, name='lista_circulaciones_filtro'),
    path('lista/circulaciones/tipo/<str:tipo>', views.lista_circulaciones, name='lista_circulaciones_filtro'),
    path('del/circulaciones/<int:circulacion_id>', views.eliminar_circulacion, name='eliminar_circulacion'),
    path('reactivar/circulacion/<int:circulacion_id>', views.reactivar_circulacion, name='reactivar_circulacion'),
    path('email/circulaciones/<int:circulacion_id>', views.circulacion_enviar_email, name='circulacion_enviar_email'),
    #Control de Fronteras
    path('circ/control/frontera', views.control_circulacion, name='control_circulacion'),
    path('circ/panel/<str:token>', views.panel_circulacion, name='panel_circulacion'),
    path('circ/control/iniciar/<int:circulacion_id>', views.iniciar_control_circulacion, name='iniciar_control_circulacion'),
    path('circ/control/finalizar/<int:registro_id>', views.finalizar_control_circulacion, name='finalizar_control_circulacion'),
    path('circ/lista/frontera', views.lista_frontera, name='lista_frontera'),
]
