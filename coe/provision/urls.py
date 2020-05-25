from django.conf.urls import url
from django.urls import path

#Import personales
from . import views as views

app_name = 'provision'

urlpatterns = [
    #Menu
    path('', views.menu_provision, name='menu_provision'),
    #Basicas:    
    path('pcoca/', views.pedir_coca, name='pedir_coca'),   
    path('peticion_persona/', views.peticion_persona, name='peticion_persona'),
    path('mod/peticion_persona/<int:peticion_id>', views.peticion_persona, name='mod_peticion_persona'),
    path('cargar/cargar_people/<int:peticion_id>', views.cargar_people, name='cargar_people'),
    path('finalizar/peticion/<int:peticion_id>', views.finalizar_peticion, name='finalizar_peticion'),
    path('peticion/<str:token>', views.ver_peticion_persona, name='ver_peticion_persona'),
    path('mod/people/<int:peticion_id>/<int:individuo_id>', views.cargar_people, name='mod_people'),
    path('del/peticion/<int:peticion_id>/<int:individuo_id>', views.quitar_persona, name='quitar_persona'),
    #Ingresos
    path('', views.menu_provision, name='menu_peticiones'),    
    path('lista/peticiones/completas', views.lista_peticiones_completas, name='lista_peticiones_completas'),
    path('lista/peticiones', views.lista_peticiones, name='lista_peticiones'),
]
