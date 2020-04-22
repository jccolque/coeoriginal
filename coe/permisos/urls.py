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
    path('cargar/dut/<int:ingreso_id>', views.cargar_dut, name='cargar_dut'),
    path('cargar/plan_vuelo/<int:ingreso_id>', views.cargar_plan_vuelo, name='cargar_plan_vuelo'),
    path('del/ingresante/<int:ingreso_id>/<int:individuo_id>', views.quitar_ingresante, name='quitar_ingresante'),
    path('ingreso/aprobado/<str:token>', views.ver_ingreso_aprobado, name='ver_ingreso_aprobado'),
    #Administracion
    #Permisos
    path('', views.menu_permisos, name='menu_permisos'),
    path('lista/activos', views.lista_activos, name='lista_activos'),
    path('lista/vencidos', views.lista_vencidos, name='lista_vencidos'),
    path('ver/permiso/<int:permiso_id>/<int:individuo_id>', views.ver_permiso, name='ver_permiso'),
    path('eliminar/permiso/<int:permiso_id>', views.eliminar_permiso, name='eliminar_permiso'),
    #Ingresos
    path('situacion/ingresos', views.situacion_ingresos, name='situacion_ingresos'),
    path('lista/ingresos', views.lista_ingresos, name='lista_ingresos'),
    path('lista/ingresos/estado/<str:estado>', views.lista_ingresos, name='lista_ingresos_filtro'),
    path('lista/ingresos/tipo/<str:tipo>', views.lista_ingresos, name='lista_ingresos_filtro'),
    path('aprobar/ingreso/<int:ingreso_id>', views.aprobar_ingreso, name='aprobar_ingreso'),
    path('del/ingreso/<int:ingreso_id>', views.eliminar_ingreso, name='eliminar_ingreso'),
    path('email/ingreso/<int:ingreso_id>', views.enviar_email, name='enviar_email'),
]