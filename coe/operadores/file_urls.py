#imports django
from django.urls import path
#Import de modulos personales
from . import file_views

app_name = 'filepaths'
urlpatterns = [
    #documentos
    path('documentos/<str:filename>', file_views.ver_documento, name='ver_documento'),
    #informacion
    path('informacion/archivos/<str:filename>', file_views.ver_archivo, name='ver_archivo'),
    path('informacion/individuos/<str:filename>', file_views.ver_foto_individuo, name='ver_foto_individuo'),
    path('informacion/individuos/documentos/<str:filename>', file_views.ver_doc_individuo, name='ver_doc_individuo'),
    #Operador
    path('operadores/<str:filename>', file_views.ver_operador, name='ver_operador'),
    #Inscripciones
    path('inscripciones/dni/<str:filename>', file_views.ver_dni_inscripto, name='ver_dni_inscripto'),
    path('inscripciones/titulo/<str:filename>', file_views.ver_titulo_inscripto, name='ver_titulo_inscripto'),
]