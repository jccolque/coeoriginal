#imports django
from django.urls import path
#Import de modulos personales
from . import permisos_views as permisos_views

#Definimos paths de la app
app_name = 'permisos_urls'
urlpatterns = [
    #Publico
    path('buscar/', permisos_views.buscar_permiso, name='buscar_permiso'),
    path('permiso/<int:individuo_id>/<int:num_doc>/', permisos_views.pedir_permiso, name='pedir_permiso'),
    path('completar/datos/<int:individuo_id>', permisos_views.completar_datos, name='completar_datos'),
    path('subir/foto/<int:individuo_id>', permisos_views.subir_foto, name='subir_foto'),
    #Administracion
    path('', permisos_views.menu_permisos, name='menu_permisos'),
    path('lista/activos', permisos_views.lista_activos, name='lista_activos'),
    path('lista/vencidos', permisos_views.lista_vencidos, name='lista_vencidos'),
    path('ver/permiso/<int:permiso_id>', permisos_views.ver_permiso, name='ver_permiso'),
    path('eliminar/permiso/<int:permiso_id>', permisos_views.eliminar_permiso, name='eliminar_permiso'),

]