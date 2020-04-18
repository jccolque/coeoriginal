#imports django
from django.urls import path
#Import de modulos personales
from . import views as views

#Definimos paths de la app
app_name = 'permisos_urls'
urlpatterns = [
    #Publico
    path('buscar/', views.buscar_permiso_web, name='buscar_permiso'),
    path('permiso/<int:individuo_id>/<int:num_doc>/', views.pedir_permiso_web, name='pedir_permiso'),
    path('completar/datos/<int:individuo_id>', views.completar_datos, name='completar_datos'),
    path('subir/foto/<int:individuo_id>', views.subir_foto, name='subir_foto'),
    #Administracion
    path('', views.menu_permisos, name='menu_permisos'),
    path('lista/activos', views.lista_activos, name='lista_activos'),
    path('lista/vencidos', views.lista_vencidos, name='lista_vencidos'),
    path('ver/permiso/<int:permiso_id>/<int:individuo_id>', views.ver_permiso, name='ver_permiso'),
    path('eliminar/permiso/<int:permiso_id>', views.eliminar_permiso, name='eliminar_permiso'),

]