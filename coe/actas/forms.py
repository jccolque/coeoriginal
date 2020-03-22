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
        choices=[],
        widget=CheckboxSelectMultiple(attrs={'class':'multiplechoice',}), 
    )
    class Meta:
        model = Acta
        fields= '__all__'
        exclude = ('fecha', 'usuario', )
    #Definimos los choices para que no crashee la db
    def __init__(self, *args, **kwargs):
        self.base_fields['participes'].choices = [(o.id,o.apellidos+', '+o.nombres) for o in Operador.objects.all()]
        super(CrearActaForm, self).__init__(*args, **kwargs)