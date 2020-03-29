#Imports Python
from datetime import date
#Imports Django
from django import forms
#Imports extra

#Imports del proyecto

#Imports de la app
from .models import Grafico, Columna, Dato

#Definimos nuestros forms
class GraficoForm(forms.ModelForm):
    class Meta:
        model = Grafico
        fields= '__all__'
        exclude = ('publico', 'update')
    def __init__(self, *args, **kwargs):
        super(GraficoForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['nombre'].widget.attrs['readonly'] = True

class ColumnaForm(forms.ModelForm):
    class Meta:
        model = Columna
        fields= '__all__'
        widgets = {
            'grafico': forms.TextInput(attrs={'readonly':'readonly'}),
        }
    def __init__(self, *args, **kwargs):
        super(ColumnaForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['nombre'].widget.attrs['readonly'] = True

class DatoForm(forms.ModelForm):
    class Meta:
        model = Dato
        fields= '__all__'
        widgets = {
            'columna': forms.HiddenInput(),
        }