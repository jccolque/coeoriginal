#Imports Python
from datetime import date
#Imports Django
from django import forms
#Imports extra

#Imports del proyecto

#Imports de la app
from .models import Grafico, Dato

#Definimos nuestros forms
class GraficoForm(forms.ModelForm):
    class Meta:
        model = Grafico
        fields= '__all__'
        exclude = ('publico', 'update')

class DatoForm(forms.ModelForm):
    class Meta:
        model = Dato
        fields= '__all__'
        exclude = ('grafico', 'update')