#Imports Django
from django import forms
#Imports extra
#Imports de la app

#Definimos nuestros forms aqui:
class ConfigGeoForm(forms.Form):
    intervalo = forms.IntegerField(label="Intervalo entre Trackings")
    distancia_alerta = forms.IntegerField(label="Distancia de Alerta")
    distancia_critica = forms.IntegerField(label="Distancia Critica")