#Imports Python
from datetime import timedelta
#Imports Django
from django import forms
from django.utils import timezone
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
#Imports de la app
from .models import Individuo, Permiso

#Formularios
class DatosForm(forms.ModelForm):
    class Meta:
        model = Individuo
        fields= ('apellidos', 'nombres', 'fecha_nacimiento', 'telefono', 'email')
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(attrs={'autocomplete':'off'}),
            'nacionalidad': autocomplete.ModelSelect2(url='georef:nacionalidad-autocomplete'),
        }

class FotoForm(forms.ModelForm):
    class Meta:
        model = Individuo
        fields= ('fotografia', )

class BuscarPermiso(forms.Form):
    num_doc = forms.CharField(label="Num Doc", required=True)
    apellido = forms.CharField(label="Apellido", required=True)

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields= '__all__'
        exclude = ('localidad', 'habilitado', 'endda')
        widgets = {
            'individuo': forms.HiddenInput(),
            'begda': XDSoftDateTimePickerInput(attrs={'label':'Fecha Ideal', 'autocomplete':'off'}, ),
        }