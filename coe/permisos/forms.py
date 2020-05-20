#Imports Python
#Imports Django
from django import forms
from django.utils import timezone
from django.forms.models import inlineformset_factory
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
from georef.models import Localidad
from informacion.models import Individuo
#Imports de la app
from .choices import TIPO_PERMISO, FRONTERA_CONTROL
from .models import NivelRestriccion, Permiso, IngresoProvincia, CirculacionTemporal
from .models import RegistroCirculacion, PasajeroCirculacion
#Formularios
class NivelRestriccionForm(forms.ModelForm):
    class Meta:
        model = NivelRestriccion
        fields= '__all__'

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

class PermisoForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=TIPO_PERMISO[:-1])#Eliminamos permiso Permanente de la lista
    class Meta:
        model = Permiso
        fields= '__all__'
        exclude = ('localidad', 'habilitado', 'endda')
        widgets = {
            'individuo': forms.HiddenInput(),
            'begda': XDSoftDateTimePickerInput(attrs={'label':'Fecha Ideal', 'autocomplete':'off'}, ),
        }

class IngresoProvinciaForm(forms.ModelForm):
    class Meta:
        model = IngresoProvincia
        fields= '__all__'
        exclude = ('fecha', 'token', 'individuos', 'estado', 'plan_vuelo', 'dut', 'operador', 'qrpath')
        widgets = {
            'fecha_llegada': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}, ),
            'origen': autocomplete.ModelSelect2(url='georef:provincia-autocomplete'),
            'destino': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class IngresoProvinciaForm(forms.ModelForm):
    class Meta:
        model = IngresoProvincia
        fields= '__all__'
        exclude = ('fecha', 'token', 'individuos', 'estado', 'permiso_nacional', 'plan_vuelo', 'dut', 'operador', 'qrpath')
        widgets = {
            'fecha_llegada': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}, ),
            'origen': autocomplete.ModelSelect2(url='georef:provincia-autocomplete'),
            'destino': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class CirculacionTemporalForm(forms.ModelForm):
    class Meta:
        model = CirculacionTemporal
        fields= ('tipo', 'email_contacto', 'marca', 'modelo', 'patente', 'titular', 'origen', 'destino', 'actividad')
        exclude = ('chofer', 'acompañante', 'permiso_nacional', 'licencia_conducir', 'fecha', 'token', 'estado', 'operador', 'qrpath')
        widgets = {
            'origen': autocomplete.ModelSelect2(url='georef:provincia-autocomplete'),
            'destino': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class IngresanteForm(forms.ModelForm):
    #Domicilio actual
    dom_origen = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Calle Numero, Localidad, Provincia'}))
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
            'num_doc', 'apellidos', 'nombres', 'sexo', 'fecha_nacimiento', 'nacionalidad', 'dom_origen', 'telefono', 'email',
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

class TemporalesForm(forms.ModelForm):
    #Domicilio actual
    dom_origen = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Calle Numero, Localidad, Provincia'}))
    #Documentos
    frente_dni = forms.FileField(required=True)
    reverso_dni = forms.FileField(required=True)
    #Base Individuo
    class Meta:
        model = Individuo
        fields= (
            'num_doc', 'apellidos', 'nombres', 'sexo', 'fecha_nacimiento', 'nacionalidad', 'dom_origen', 'telefono', 'email',
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

class DUTForm(forms.ModelForm):
    class Meta:
        model = IngresoProvincia
        fields= ('dut',)

class PlanVueloForm(forms.ModelForm):
    class Meta:
        model = IngresoProvincia
        fields= ('plan_vuelo',)

class AprobarForm(forms.Form):
    fecha = forms.DateTimeField(label="Fecha Aprobada", 
        required=True, 
        widget=XDSoftDateTimePickerInput()
    )

class SearchCirculacion(forms.Form):
    num_doc = forms.CharField(label="Documento de Identidad", required=False)
    patente = forms.CharField(label="Dominio", required=False)

class InicioCirculacionForm(forms.Form):
    control = forms.ChoiceField(choices=FRONTERA_CONTROL, label="Punto Fronterizo")
    destino = forms.ModelChoiceField(
        label="Destino de la Circulacion",
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=True,
    )
    cant_inicio = forms.IntegerField(label="Cantidad Pasajeros")
    tiempo_permitido = forms.IntegerField(label="Tiempo Permitido")

class FinalCirculacionForm(forms.Form):
    control = forms.ChoiceField(choices=FRONTERA_CONTROL, label="Punto Fronterizo")
    cant_final = forms.IntegerField(label="Cantidad Pasajeros")
    aclaraciones = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))

PasajeroFormset = inlineformset_factory(
    RegistroCirculacion,
    PasajeroCirculacion,
    fields=('num_doc', 'salio'),
    extra=2,
    can_delete=True,
)