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
from .choices import TIPO_COMUNIDAD, TIPO_PROFESIONAL, GRUPO_SANGUINEO, TIPO_CONDICION
from .models import ProyectoEstudiantil, Turno
from .models import PeticionCoca
from .models import Organization, DomicilioOrganizacion

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

class PeticionForm(forms.ModelForm):
    #Datos del Pedido
    destino = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    comunidad = forms.ChoiceField(choices=TIPO_COMUNIDAD, initial='NO')
    #Domicilio en jujuy
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
    frente_dni = forms.FileField(required=False)
    reverso_dni = forms.FileField(required=False)
    #Base Individuo
    class Meta:
        model = Individuo
        fields = (
            'num_doc', 'apellidos', 'nombres', 'sexo', 'fecha_nacimiento', 'nacionalidad', 'telefono', 'email',
            'dom_localidad', 'dom_calle', 'dom_numero', 'dom_aclaracion',
            'destino', 'comunidad',
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

class AprobarPersonaForm(forms.ModelForm):
    destino = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    #Base Individuo
    class Meta:
        model = Individuo
        fields = (
            'num_doc', 'apellidos', 'nombres', 
        )
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        if self.instance.pk:
            self.fields['num_doc'].widget.attrs.update({'readonly': True})
            self.fields['nombres'].widget.attrs.update({'readonly': True})
            self.fields['apellidos'].widget.attrs.update({'readonly': True})

#Formularios
class OrganizationForm(forms.ModelForm):
    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    barrio = forms.CharField(required=True, )
    calle = forms.CharField(required=True, )
    numero = forms.CharField(required=True, )
    manzana = forms.CharField(required=False, )
    lote = forms.CharField(required=False, )
    piso = forms.CharField(required=False, )      
    class Meta:
        model = Organization
        fields= '__all__'   
        exclude = ('responsables','afiliados', 'token', 'fecha', 'estado', 'operador', 'archivo_adjunto')     
        widgets = {
            'cuit': forms.TextInput(attrs={'placeholder': 'Introduzca CUIT'}),
            'denominacion': forms.TextInput(attrs={'placeholder': 'Introduzca Denominacion'}),
            'tipo_organizacion': forms.Select(attrs={'placeholder': 'Seleccione Tipo de Organizacion'}),
            'fecha_constitucion': XDSoftDatePickerInput(attrs={'autocomplete':'off'}),
            'cantidad': forms.TextInput(attrs={'placeholder': 'Introduzca Cantidad de Afiliados'}),
            'mail_institucional': forms.TextInput(attrs={'placeholder': 'Introduzca MAIL INSTITUCIONAL'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Introduzca Telefono Institucional'}),            
            'celular': forms.TextInput(attrs={'placeholder': 'Introduzca Celular Institucional'}),                       
            'descripcion ': forms.Textarea(attrs={'placeholder': 'Describa el Objeto de su Organizacion'}),                    
        }

class AfiliadoForm(forms.ModelForm):
    #Domicilio en jujuy
    dom_localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    dom_calle = forms.CharField(required=True, )
    dom_numero = forms.CharField(required=True, )
    dom_aclaracion = forms.CharField(required=False, )
    #Datos Organizacionales
    tipo_cond = forms.ChoiceField(choices=TIPO_CONDICION, required=True, label="Condicion Poblacional")
    rol = forms.CharField(required=False, label="Rol Institucional")
    #Documentos
    frente_dni = forms.FileField(required=False)
    reverso_dni = forms.FileField(required=False)
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

class DocumentacionForm(forms.Form):
    documentacion = forms.FileField()

class AprobarOrgForm(forms.ModelForm):
    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    calle = forms.CharField(required=True, )
    #Base Individuo
    class Meta:
        model = Organization
        fields = (
            'cuit', 'denominacion', 'tipo_organizacion', 
        )
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        if self.instance.pk:
            self.fields['cuit'].widget.attrs.update({'readonly': True})            
            self.fields['denominacion'].widget.attrs.update({'readonly': True})
            self.fields['calle'].widget.attrs.update({'readonly': True})