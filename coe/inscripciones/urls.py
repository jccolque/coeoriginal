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
    path('ver/capacitacion/<int:inscripto_id>/<int:capacitacion_id>', views.ver_capacitacion, name='ver_capacitacion'),
    #Turnos
    path('turnero/editar/<int:ubicacion_id>', views.editar_turnos, name='editar_turnos'),
    url(r'turnero/bajar/(?P<ubicacion_id>[0-9]+)/(?P<fecha>\d{4}-\d{2}-\d{2})/(?P<hora>\d{2}:\d{2})/$', views.bajar_turno, name='bajar_turno'),
    path('turnero/<int:ubicacion_id>/<int:inscripto_id>/', views.turnero, name='turnero'),
    url(r'turnero/(?P<ubicacion_id>[0-9]+)/(?P<inscripto_id>[0-9]+)/(?P<fecha>\d{4}-\d{2}-\d{2})/(?P<hora>\d{2}:\d{2})/$', views.turnero, name='turno_seleccionado'),
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
    path('proyecto/aval/<str:token>/', views.cargar_aval_institucional, name='cargar_aval_institucional'),
    path('proyecto/responsable/<str:token>/', views.cargar_responsable_institucional, name='cargar_responsable_institucional'),
    path('proyecto/responsable/<str:token>/<int:individuo_id>', views.cargar_responsable_institucional, name='mod_responsable_institucional'),
    path('proyecto/voluntario/<str:token>/', views.cargar_voluntario, name='cargar_voluntario'),
    path('mod/voluntario/<str:token>/<int:individuo_id>', views.cargar_voluntario, name='mod_voluntario_proyecto'),
    path('del/voluntario/<str:token>/<int:individuo_id>', views.quitar_voluntario_proyecto, name='quitar_voluntario_proyecto'),
    path('proyecto/cargar/tutor/<str:token>/<int:voluntario_id>', views.cargar_tutor, name='cargar_tutor'),
    path('proyecto/cargar/autorizacion/<str:token>/<int:voluntario_id>', views.cargar_autorizacion, name='cargar_autorizacion'),
    #Activacion:
    path('act/<int:inscripcion_id>/<int:num_doc>', views.activar_inscripcion, name='activar_inscripcion'),
]