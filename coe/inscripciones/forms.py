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
from .models import ProyectoEstudiantil

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

class ProyectoEstudiantilForm(forms.ModelForm):
    class Meta:
        model = ProyectoEstudiantil
        fields= '__all__'
        exclude = ('escuela_aval', 'responsable', 'voluntarios', 'token', 'estado', 'fecha',)
        #widgets = {
        #    'escuela_localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        #}

class IndividuoForm(forms.ModelForm):
    #Domicilio en jujuy
    dom_localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    dom_calle = forms.CharField(required=True, )
    dom_numero = forms.CharField(required=True, )
    dom_aclaracion = forms.CharField(required=False, )
    #Documentos
    frente_dni = forms.FileField(required=True)
    reverso_dni = forms.FileField(required=True)
    #Base Individuo
    class Meta:
        model = Individuo
        fields= (
            'num_doc', 'apellidos', 'nombres', 'sexo', 'fecha_nacimiento', 'nacionalidad', 'telefono', 'email',
            'dom_localidad', 'dom_calle', 'dom_numero', 'dom_aclaracion',
            'frente_dni', 'reverso_dni',
        )
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(attrs={'autocomplete':'off'}),
            'nacionalidad': autocomplete.ModelSelect2(url='georef:nacionalidad-autocomplete'),
        }
    def clean(self):
        if self.cleaned_data['telefono'] is None or self.cleaned_data['telefono'] == '+549388':
            raise forms.ValidationError("Debe cargar un telefono.")
        else:
            return self.cleaned_data