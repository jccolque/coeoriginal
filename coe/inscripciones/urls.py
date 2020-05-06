#imports django
from django.urls import path
from django.conf.urls import url
#Import de modulos personales
from . import views

#Definimos paths de la app
app_name = 'inscripciones'
urlpatterns = [
    #Publico
    path('profesional/salud', views.inscripcion_salud, name='inscripcion_salud'),
    path('voluntario/social', views.inscripcion_social, name='inscripcion_social'),
    path('proyecto/estudiantil', views.inscripcion_proyecto, name='inscripcion_proyecto'),
    path('foto/<int:inscripcion_id>', views.subir_foto, name='subir_foto'),
    path('frente_dni/<int:inscripcion_id>', views.cargar_frente_dni, name='cargar_frente_dni'),
    path('reverso_dni/<int:inscripcion_id>', views.cargar_reverso_dni, name='cargar_reverso_dni'),
    path('ver/<int:inscripcion_id>/<str:num_doc>', views.ver_inscripto, name='ver_inscripto'),
    #Administracion
    path('', views.menu, name='menu'),
    path('lista/tareas', views.lista_tareas, name='lista_tareas'),
    path('lista/<str:tipo_inscripto>/', views.lista_voluntarios, name='lista_voluntarios'),
    path('lista/tarea/<str:tarea_id>/', views.lista_por_tarea, name='lista_por_tarea'),
    path('lista/proyectos', views.lista_proyectos, name='lista_proyectos'),
    path('avanzar/estado/<int:inscripcion_id>', views.avanzar_estado, name='avanzar_estado'),
    path('inscripto/email/<int:inscripcion_id>', views.enviar_email, name='enviar_email'),
    #Proyecto
    path('proyecto/panel/<str:token>/', views.panel_proyecto, name='panel_proyecto'),

    #Activacion:
    path('act/<int:inscripcion_id>/<int:num_doc>', views.activar_inscripcion, name='activar_inscripcion'),
]