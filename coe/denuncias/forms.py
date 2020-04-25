#Imports Python
#Imports Django
from django import forms
#Imports extra
#Imports del proyecto
from core.widgets import XDSoftDateTimePickerInput
from core.models import Aclaracion
#Imports de la app
from .choices import ESTADO_DENUNCIA

class EvolucionarForm(forms.ModelForm):
    estado = forms.ChoiceField(choices=ESTADO_DENUNCIA, required=True)
    class Meta:
        model = Aclaracion
        fields= '__all__'
        exclude = ('modelo', 'operador', )
        widgets = {
            'fecha': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }