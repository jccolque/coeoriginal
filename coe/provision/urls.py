from django.conf.urls import url
from django.urls import path

#Import personales
from . import views as views

app_name = 'provision'

urlpatterns = [
    #Basicas:    
    path('pcoca/', views.pedir_coca, name='pedir_coca'),
    path('disclaimero/', views.disclaimer_org, name='disclaimer_org'),
]