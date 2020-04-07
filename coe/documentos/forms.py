#Imports Python
from datetime import date
#Imports Django
from django.utils import timezone
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
#Imports de la app
from .models import Documento, Version

#Definimos nuestros forms
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = '__all__'
        exclude = ('publico', )
        widgets = {
            'subcomite': autocomplete.ModelSelect2(url='operadores:subcomite-autocomplete'),
        }

class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = '__all__'
        exclude = ('fecha', )
        widgets = {
            'documento': forms.HiddenInput(),
            'operador': forms.HiddenInput(),
        }