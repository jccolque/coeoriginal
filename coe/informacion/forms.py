#Imports Python
from datetime import date
#Imports Django
from django.utils import timezone
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.forms.widgets import CheckboxSelectMultiple
#Imports extra
from dal import autocomplete
#Imports del proyecto

#Imports de la app
from .models import Archivo, Vehiculo
from .models import Individuo, Domicilio, Atributo, Sintoma

#Definimos nuestros forms
class ArchivoForm(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['tipo', 'nombre', 'archivo', ]
        widgets = {
            #'descripcion': forms.Textarea(attrs={'cols': 40, 'rows': 10}),
        }

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields= '__all__'
        exclude = ('fecha', 'usuario',)

class IndividuoForm(forms.ModelForm):
    class Meta:
        model = Individuo
        fields= '__all__'

class SearchIndividuoForm(forms.Form):
    num_doc = forms.IntegerField(required=False)
    apellidos = forms.CharField(required=False)

class DomicilioForm(forms.ModelForm):
    class Meta:
        model = Domicilio
        fields= '__all__'
        exclude = ('individuo', )
        widgets = {
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class AtributoForm(forms.ModelForm):
    class Meta:
        model = Atributo
        fields= '__all__'
        exclude = ('individuo', 'activo', )
        widgets = {
            'tipo': autocomplete.ModelSelect2(url='informacion:atributos-autocomplete'),
        }

class SintomaForm(forms.ModelForm):
    class Meta:
        model = Sintoma
        fields= '__all__'
        exclude = ('individuo', )
        widgets = {
            'tipo': autocomplete.ModelSelect2(url='informacion:sintomas-autocomplete'),
        }