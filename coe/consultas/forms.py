#Imports Python
#Imports Django
from django import forms
#Imports extra
#Imports del proyecto
#Imports de la app
from .models import Consulta, Respuesta

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
