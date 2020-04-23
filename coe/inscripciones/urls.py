#imports django
from django.urls import path
from django.conf.urls import url
#Import de modulos personales
from . import views
#from . import autocomplete

#Definimos paths de la app
app_name = 'inscripciones'
urlpatterns = [
    #Publico
    path('profesional/salud', views.inscripcion_salud, name='inscripcion_salud'),
    path('voluntario/social', views.inscripcion_social, name='inscripcion_social'),
    #Administracion
    path('', views.menu, name='menu'),
    path('lista/<str:tipo_inscripto>/', views.lista_voluntarios, name='lista_voluntarios'),

    path('ver/<int:inscripto_id>', views.ver_inscripto, name='ver_inscripto'),
    path('download', views.download_inscriptos, name='download_inscriptos'),

    #Activacion:
    path('act/<int:inscripcion_id>', views.activar_inscripcion, name='activar_inscripcion'),
    #url(r'^act/(?P<inscripcion_id>[0-9]+)/(?P<token>[0-9A-Za-z]{1,35})/$', views.activar_inscripcion, name='activar_inscripcion'),
]