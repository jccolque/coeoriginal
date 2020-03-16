from django.conf.urls import url
from django.urls import path
from . import views
from . import autocomplete

app_name = 'georef'
urlpatterns = [
    #Administrador
    path('upload', views.upload_localidades, name='upload_localidades'),

    #Autocompleteviews
    url(r'^departamento-autocomplete/$', autocomplete.DepartamentoAutocomplete.as_view(), name='departamento-autocomplete',),
    url(r'^localidad-autocomplete/$', autocomplete.LocalidadAutocomplete.as_view(), name='localidad-autocomplete',),
    url(r'^barrio-autocomplete/$', autocomplete.BarrioAutocomplete.as_view(), name='barrio-autocomplete',),
]