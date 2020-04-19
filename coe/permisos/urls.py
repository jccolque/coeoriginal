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
    path('ingreso/<str:token>', views.ver_ingreso_provincial, name='ver_ingreso_provincial'),
    path('cargar/ingresantes/<int:ingreso_id>', views.cargar_ingresante, name='cargar_ingresantes'),
    path('cargar/dut/<int:ingreso_id>', views.cargar_dut, name='cargar_dut'),
    path('cargar/plan_vuelo/<int:ingreso_id>', views.cargar_plan_vuelo, name='cargar_plan_vuelo'),
    #Administracion
    #Permisos
    path('', views.menu_permisos, name='menu_permisos'),
    path('lista/activos', views.lista_activos, name='lista_activos'),
    path('lista/vencidos', views.lista_vencidos, name='lista_vencidos'),
    path('ver/permiso/<int:permiso_id>/<int:individuo_id>', views.ver_permiso, name='ver_permiso'),
    path('eliminar/permiso/<int:permiso_id>', views.eliminar_permiso, name='eliminar_permiso'),
    #Ingresos
    path('lista/ingresos', views.lista_ingresos, name='lista_ingresos'),
]