#Imports Python
#Imports Django
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
#Imports extra
#Imports del proyecto
from operadores.models import Operador
#Imports de la app
from .models import Acta

#Definimos nuestros forms
class CrearActaForm(forms.ModelForm):
    participes = forms.MultipleChoiceField(
        label='Participes',
        choices=[(o.id,o.usuario.last_name+', '+o.usuario.first_name) for o in Operador.objects.all()],
        widget=CheckboxSelectMultiple(attrs={'class':'multiplechoice',}), 
    )
    class Meta:
        model = Acta
        fields= '__all__'
        exclude = ('fecha', 'usuario', )