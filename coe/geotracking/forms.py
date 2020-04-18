#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
from informacion.models import Individuo
#Imports de la app
from .models import GeOperador

#Definimos nuestros forms aqui:
class ConfigGeoForm(forms.Form):
    intervalo = forms.IntegerField(label="Intervalo entre Trackings")
    distancia_alerta = forms.IntegerField(label="Distancia de Alerta")
    distancia_critica = forms.IntegerField(label="Distancia Critica")

class NuevoGeoOperador(forms.ModelForm):
    class Meta:
        model = GeOperador
        fields= '__all__'
        exclude = ('controlados', )
        widgets = {
            'operador': autocomplete.ModelSelect2(url='operadores:operadores-autocomplete'),
        }

class NuevoIndividuo(forms.Form):
    individuo = forms.ModelChoiceField(
        queryset= Individuo.objects.all(),
        required= True,
        widget= autocomplete.ModelSelect2(url='geotracking:individuostrackeados-autocomplete'),
    )