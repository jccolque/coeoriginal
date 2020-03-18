#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
from . import autocomplete

#Definimos paths de la app
app_name = 'tareas'
urlpatterns = [
    path('', views.menu, name='menu'),
    #Basicas:
    path('lista', views.lista_tareas, name='lista_tareas'),
    path('ver/<int:tarea_id>', views.ver_tarea, name='ver_tarea'),
    path('crear', views.crear_tarea, name='crear_tarea'),
    path('mod/<int:tarea_id>', views.crear_tarea, name='mod_tarea'),
    path('eliminar/tarea/<int:tarea_id>', views.eliminar_tarea, name='eliminar_tarea'),

    path('agregar/responsable/<int:tarea_id>', views.agregar_responsable, name='agregar_responsable'),
    path('eliminar/responsable/<int:responsable_id>', views.eliminar_responsable, name='eliminar_responsable'),
    path('agregar/evento/<int:tarea_id>', views.agregar_evento, name='agregar_evento'),
    path('eliminar/evento/<int:evento_id>', views.eliminar_evento, name='eliminar_evento'),
    #Autocomplete
    url(r'^tareas-autocomplete/$', autocomplete.TareasAutocomplete.as_view(), name='tareas-autocomplete',),
]