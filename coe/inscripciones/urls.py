#imports django
from django.urls import path
from django.conf.urls import url
#Import de modulos personales
from . import views
#from . import autocomplete

#Definimos paths de la app
app_name = 'inscripciones'
urlpatterns = [
    path('', views.menu, name='menu'),

    path('cargar', views.cargar_inscripcion, name='cargar_inscripcion'),
    path('lista', views.lista_inscriptos, name='lista_inscriptos'),
    path('lista/prof/<int:profesion_id>', views.lista_inscriptos, name='lista_filtrada'),
    path('ver/<int:inscripto_id>', views.ver_inscripto, name='ver_inscripto'),
    path('download', views.download_inscriptos, name='download_inscriptos'),

    #Activacion:
    url(r'^act/(?P<inscripcion_id>[0-9]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activar_inscripcion_mail, name='activar_inscripcion_mail'),
]