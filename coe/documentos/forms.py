#Imports Python
from datetime import date
#Imports Django
from django.utils import timezone
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
#Imports de la app
from .models import Documento

#Definimos nuestros forms
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = '__all__'
        widgets = {
            'subcomite': autocomplete.ModelSelect2(url='operadores:subcomite-autocomplete'),
        }