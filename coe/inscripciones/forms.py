#Imports Python
#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.widgets import XDSoftDatePickerInput
#Imports de la app
from .models import Inscripto

#Definimos nuestros forms
class ProfesionalSaludForm(forms.ModelForm):
    class Meta:
        model = Inscripto
        fields= '__all__'
        exclude = ('tipo_inscripto', 'grupo_sanguineo', 'fecha', 'valido', 'disponible', 'oficio')
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(),
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class VoluntarioSocialForm(forms.ModelForm):
    no_grupo_riesgo = forms.BooleanField(required=True)
    no_aislamiento = forms.BooleanField(required=True)
    class Meta:
        model = Inscripto
        fields= '__all__'
        exclude = ('tipo_inscripto', 'fecha', 'valido', 'disponible')
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(),
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }