#Imports Python
#Imports Django
from django import forms
#Imports extra

#Imports del proyecto

#Imports de la app
from .models import Inscripto

#Definimos nuestros forms
class ProfesionalSaludForm(forms.ModelForm):
    class Meta:
        model = Inscripto
        fields= '__all__'
        exclude = ('tipo_inscripto', 'fecha', 'valido', 'disponible')
        