#Import Standard de django
from django import forms
#imports del proyecto

#Definimos forms
class SearchForm(forms.Form):
    buscar = forms.CharField(label="", required=True)