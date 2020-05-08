#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
from informacion.models import Individuo
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
#Imports de la app
from .models import Seguimiento, Vigia
from .functions import obtener_bajo_seguimiento

#Definimos nuestros forms aqui:
class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields= '__all__'
        exclude = ('individuo', )
        widgets = {
            'fecha': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }

class NuevoVigia(forms.ModelForm):
    class Meta:
        model = Vigia
        fields= '__all__'
        exclude = ('controlados', )
        widgets = {
            'operador': autocomplete.ModelSelect2(url='operadores:operadores-autocomplete'),
        }

class NuevoIndividuo(forms.Form):
    individuo = forms.ModelChoiceField(
        queryset= obtener_bajo_seguimiento(),
        required= True,
        widget= autocomplete.ModelSelect2(url='seguimiento:individuosvigilados-autocomplete'),
    )

class AsignarVigia(forms.Form):
    vigia = forms.ModelChoiceField(
        queryset=Vigia.objects.all(),
        required=True,
        widget= autocomplete.ModelSelect2(url='seguimiento:vigias-autocomplete'),
    )
