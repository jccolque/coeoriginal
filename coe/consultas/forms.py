#Imports Python
#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.widgets import XDSoftDateTimePickerInput
from core.models import Aclaracion
#Imports de la app
from .choices import ESTADO_DENUNCIA
from .models import Telefonista
from .models import Consulta, Respuesta
from .models import Llamada

#Definimos nuestros formularios
class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['autor', 'email', 'telefono', 'asunto', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'cols': 40, 'rows': 10}),
        }

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ['respuesta', ]

class NuevoTelefonistaForm(forms.ModelForm):
    class Meta:
        model = Telefonista
        fields= '__all__'
        exclude = ('consultas', )
        widgets = {
            'operador': autocomplete.ModelSelect2(url='operadores:operadores-autocomplete'),
        }

class LlamadaForm(forms.ModelForm):
    class Meta:
        model = Llamada
        fields= '__all__'
        exclude = ('fecha', 'telefonista', )
        widgets = {
            'individuo': autocomplete.ModelSelect2(url='informacion:individuos-autocomplete'),
        }

class EvolucionarForm(forms.ModelForm):
    estado = forms.ChoiceField(choices=ESTADO_DENUNCIA, required=True)
    class Meta:
        model = Aclaracion
        fields= '__all__'
        exclude = ('modelo', 'operador', )
        widgets = {
            'fecha': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }