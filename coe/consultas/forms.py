#Imports Python
#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
#Imports de la app
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