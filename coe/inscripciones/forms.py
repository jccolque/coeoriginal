#Imports Python
from datetime import date
#Imports Django
from django import forms
#Imports extra

#Imports del proyecto

#Imports de la app
from .models import Inscripto

#Definimos nuestros forms
class InscriptoForm(forms.ModelForm):
    class Meta:
        model = Inscripto
        fields= '__all__'
        exclude = ('fecha', 'valido', 'disponible')