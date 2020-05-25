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
from tinymce.widgets import TinyMCE
#Imports del proyecto
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
from georef.models import Nacionalidad, Localidad, Ubicacion
from informacion.models import Individuo
#Imports de la app
from .choices import TIPO_PROFESIONAL, GRUPO_SANGUINEO
from .models import ProyectoEstudiantil, Turno
from .models import Organization, Empleado, Domic_o, Peticionp

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
        exclude = ('seguimiento_actual', 'origen', 'destino', 'observaciones', 'fotografia', 'qrpath', 'situacion_actual', 'domicilio_actual')
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
        exclude = ('seguimiento_actual', 'origen', 'destino', 'observaciones', 'fotografia', 'qrpath', 'situacion_actual', 'domicilio_actual')
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
        fields = (
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

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields= '__all__'
        exclude = ('inscripto',)
        widgets = {
            'fecha' : XDSoftDateTimePickerInput(attrs={'autocomplete':'off'})
        }
    def __init__(self, user, *args, **kwargs):
        super(TurnoForm, self).__init__(*args, **kwargs)
        #Filtramos Ubicaciones solo Atencion al publico
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(tipo='AP')
    def clean(self):
        ubicacion = self.cleaned_data['ubicacion']
        #Chequeamos dia:
        fecha = self.cleaned_data['fecha'].date()
        if fecha.weekday() > 4:
            raise forms.ValidationError("Solo se entregan turnos de lunes a viernes")
        #Chequeamos Horario
        hora = self.cleaned_data['fecha'].time()
        if hora < ubicacion.hora_inicio:
            raise forms.ValidationError("Debe ser Posterio al horario de Inicio: " + str(ubicacion.hora_inicio))
        if hora > ubicacion.hora_cierre:
            raise forms.ValidationError("Debe ser Anterior al horario de Cierre: " + str(ubicacion.hora_cierre))
        return self.cleaned_data

#COCA
class AprobarForm(forms.Form):
    fecha = forms.DateTimeField(label="Fecha Aprobada", 
        required=True, 
        widget=XDSoftDateTimePickerInput()
    )
    
class PersonapetForm(forms.ModelForm):    
    #Domicilio en jujuy
    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    calle = forms.CharField(required=True, )
    numero = forms.CharField(required=True, )
    aclaracion = forms.CharField(required=False, )
    #Documentos
    frente_dni = forms.FileField(required=True)
    reverso_dni = forms.FileField(required=True)
    #Base Individuo
    class Meta:
        model = Individuo
        fields= (
            'tipo_doc', 'num_doc', 'apellidos', 'nombres', 'sexo', 'fecha_nacimiento', 'nacionalidad', 'telefono', 'email',
            'localidad', 'calle', 'numero', 'aclaracion',
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

class PeticionpForm(forms.ModelForm):
    class Meta:
        model = Peticionp
        fields= '__all__'
        exclude = ('fecha', 'token', 'individuos', 'estado', 'operador')
        widgets = {
            'cantidad': forms.TextInput(attrs={'placeholder': 'Introduzca Cantidad'}),
            'email_contacto': forms.TextInput(attrs={'placeholder': 'Introduzca EMAIL de Contacto'}),
            'destino': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),            
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
    
# class DomincForm(forms.ModelForm):
#     class Meta:
#         model = Domic_o
#         fields = '__all__'
#         exclude = ('organizacion',)
#         widgets = {
#             'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
#         }

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'
        exclude = ('organizacion',)

EmpleadoFormset = inlineformset_factory(Organization, Empleado, EmpleadoForm, extra=10, can_delete = True)
