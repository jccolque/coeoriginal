#Imports Python
import datetime
from datetime import timedelta
#Imports Django
from django import forms
from django.utils import timezone
from django.forms.models import inlineformset_factory
from django.forms import ModelForm, modelformset_factory
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
from georef.models import Localidad
from informacion.models import Individuo
#Imports de la app
from .models import Organization, Empleado, Domic_o
from informacion.models import Individuo

class OrgaForm(forms.Form):
    cuit = forms.CharField(max_length = 13)  

class DniForm(forms.Form):
    num_doc = forms.CharField(max_length = 50)

class PersonaForm(forms.ModelForm):
    localidad = forms.ModelChoiceField(
        queryset = Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,        
    )
    calle = forms.CharField(required=False, )
    numero = forms.CharField(required=False, )
    aclaracion = forms.CharField(required=False, )    
    class Meta:
        model = Individuo        
        fields = '__all__'
        exclude = ('nacionalidad', 'origen', 'destino', 'observaciones', 'domicilio_actual', 'seguimiento_actual', 'situacion_actual', 'fotografia', 'qrpath', )
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(attrs={'autocomplete':'off'}),            
        }

#Formularios
class OrganizationForm(forms.ModelForm):
    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=False,
    )
    calle = forms.CharField(required=False, )
    numero = forms.CharField(required=False, )
    barrio = forms.CharField(required=False, )
    manzana = forms.CharField(required=False, )
    lote = forms.CharField(required=False, )
    piso = forms.CharField(required=False, )      
    class Meta:
        model = Organization
        fields= '__all__'        
        widgets = {
            'cuit': forms.TextInput(attrs={'placeholder': 'Introduzca CUIT'}),
            'denominacion': forms.TextInput(attrs={'placeholder': 'Introduzca Denominacion'}),
            'tipo_organizacion': forms.Select(attrs={'placeholder': 'Seleccione Tipo de Organizacion'}),
            'fecha_constitucion': forms.DateInput(attrs={'value': datetime.datetime.now().strftime('%d/%m/%Y')}),
            'mail_institucional': forms.TextInput(attrs={'placeholder': 'Introduzca MAIL INSTITUCIONAL'}),
            'telefono_inst1': forms.TextInput(attrs={'placeholder': 'Introduzca Telefono Institucional'}),
            'telefono_inst2': forms.TextInput(attrs={'placeholder': 'Introduzca Telefono Institucional Opcional'}),
            'celular_inst1': forms.TextInput(attrs={'placeholder': 'Introduzca Celular Institucional'}),
            'celular_inst2': forms.TextInput(attrs={'placeholder': 'Introduzca Celular Institucional Opcional'}),            
            'archivo_adjunto': forms.FileInput(attrs={'placeholder': 'Suba Informacion Respaldatoria'}),
            'descripcion ': forms.Textarea(attrs={'placeholder': 'Describa el Objeto de su Organizacion'}),                    
        }
    
class DomincForm(forms.ModelForm):
    class Meta:
        model = Domic_o
        fields = '__all__'
        exclude = ('organizacion',)
        widgets = {
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'
        exclude = ('organizacion',)

EmpleadoFormset = inlineformset_factory(Organization, Empleado, EmpleadoForm, extra=10, can_delete = True)

