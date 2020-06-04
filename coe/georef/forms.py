#Imports Python
from datetime import date
#Imports Django
from django.utils import timezone
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
#Imports de la app
from .models import Nacionalidad, Provincia, Departamento, Localidad, Barrio, Ubicacion

#Definimos nuestros forms
class NacionalidadForm(forms.ModelForm):
    class Meta:
        model = Nacionalidad
        fields = '__all__'

class ProvinciaForm(forms.ModelForm):
    class Meta:
        model = Provincia
        fields = '__all__'
        widgets = {
            'nacion': autocomplete.ModelSelect2(url='georef:nacionalidad-autocomplete'),
        }

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = '__all__'
        widgets = {
            'provincia': autocomplete.ModelSelect2(url='georef:provincia-autocomplete'),
        }

class LocalidadForm(forms.ModelForm):
    class Meta:
        model = Localidad
        fields = '__all__'
        exclude = ('publico', 'latitud', 'longitud', )
        widgets = {
            'departamento': autocomplete.ModelSelect2(url='georef:departamento-autocomplete'),
        }

class BarrioForm(forms.ModelForm):
    class Meta:
        model = Barrio
        fields = '__all__'
        exclude = ('publico', )
        widgets = {
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = '__all__'
        exclude = ('latitud', 'longitud', )
        widgets = {
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
            'barrio': autocomplete.ModelSelect2(url='georef:barrio-autocomplete'),
        }
