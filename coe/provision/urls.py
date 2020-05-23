from django.conf.urls import url
from django.urls import path

#Import personales
from . import views as views

app_name = 'provision'

urlpatterns = [
    #Basicas:    
    path('pcoca/', views.pedir_coca, name='pedir_coca'),
    path('buscorganizacion/', views.buscar_organizacion, name='buscar_organizacion'),
    path('disclaimerorg/<str:cuit>', views.disclaimer_org, name='cargar_disclaimer_org'),
    path('disclaimerorg/<int:organization_id>/<str:cuit>/', views.disclaimer_orgedit, name='editar_disclaimer_org'),
    path('buscorpersona/', views.buscar_persona, name='buscar_persona'),
    path('cargar_persona/<str:num_doc>', views.cargar_persona, name='cargar_persona'),
    path('edit_persona/<int:individuo_id>/<str:num_doc>/', views.edit_persona, name='edit_persona'),
]