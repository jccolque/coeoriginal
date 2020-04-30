#Imports Python
#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
from tinymce.widgets import TinyMCE
#Imports del proyecto
from core.widgets import XDSoftDatePickerInput
from georef.models import Localidad
from informacion.models import Individuo
#Imports de la app
from .choices import TIPO_PROFESIONAL, GRUPO_SANGUINEO

#Definimos nuestros forms
class ProfesionalSaludForm(forms.ModelForm):
    #Datos profesionales
    profesion = forms.ChoiceField(choices=TIPO_PROFESIONAL)
    matricula = forms.CharField(label="Matricula")
    frente_dni = forms.FileField(label="Foto del Dni")
    archivo_titulo = forms.FileField(label="Foto del Titulo")
    info_extra = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), required=False)
    #Domicilio
    dom_localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    dom_calle = forms.CharField(required=True, )
    dom_numero = forms.CharField(required=True, )
    dom_aclaracion = forms.CharField(required=False, )
    #Datos del individuo
    class Meta:
        model = Individuo
        fields= '__all__'
        exclude = ('origen', 'destino', 'observaciones', 'fotografia', 'qrpath', 'situacion_actual', 'domicilio_actual')
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(),
            'nacionalidad': autocomplete.ModelSelect2(url='georef:nacionalidad-autocomplete'),
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class VoluntarioSocialForm(forms.ModelForm):
    no_grupo_riesgo = forms.BooleanField(required=True)
    no_aislamiento = forms.BooleanField(required=True)
    oficio = forms.CharField(label="Oficio/Profesion")
    info_extra = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 10}), required=False)
    #Domicilio
    dom_localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    dom_calle = forms.CharField(required=True)
    dom_numero = forms.CharField(required=True)
    dom_aclaracion = forms.CharField(required=False)
    #Datos del individuo
    class Meta:
        model = Individuo
        fields= '__all__'
        exclude = ('origen', 'destino', 'observaciones', 'fotografia', 'qrpath', 'situacion_actual', 'domicilio_actual')
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(),
            'nacionalidad': autocomplete.ModelSelect2(url='georef:nacionalidad-autocomplete'),
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }