#Imports Python
#Imports Django
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
#Imports extra
from dal import autocomplete
#Imports del proyecto
from coe.settings import SECRET_KEY
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
from georef.models import Localidad
#Imports de la app
from .models import TipoAtributo, TipoSintoma
from .models import Vehiculo, ControlVehiculo
from .models import Individuo, Domicilio, Atributo, Sintoma
from .models import Situacion, Archivo, Relacion, Seguimiento, Permiso

#Definimos nuestros forms
class ArchivoForm(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['tipo', 'nombre', 'archivo', ]

class ArchivoFormWithPass(forms.ModelForm):
    passwd = forms.CharField(label="Password de Administrador", max_length=100, widget=forms.PasswordInput)
    class Meta:
        model = Archivo
        fields = ['tipo', 'nombre', 'archivo', ]
    def clean(self):
        if self.cleaned_data['passwd'] == SECRET_KEY:
            return self.cleaned_data
        else:
            raise forms.ValidationError("La contraseña ingresada es incorrecta.")

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields= '__all__'
        exclude = ('fecha', 'usuario',)

class ControlVehiculoForm(forms.ModelForm):
    class Meta:
        model = ControlVehiculo
        fields= '__all__'
        exclude = ('vehiculo', 'fecha', )

class IndividuoForm(forms.ModelForm):
    dom_localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=False,
    )
    dom_calle = forms.CharField(required=False, )
    dom_numero = forms.CharField(required=False, )
    dom_aclaracion = forms.CharField(required=False, )
    atributos = forms.MultipleChoiceField(
        choices=[],
        widget=CheckboxSelectMultiple(attrs={'class':'multiplechoice',}),
        required=False
    )
    sintomas = forms.MultipleChoiceField(
        choices=[],
        widget=CheckboxSelectMultiple(attrs={'class':'multiplechoice',}),
        required=False
    )
    class Meta:
        model = Individuo
        fields= '__all__'
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(attrs={'autocomplete':'off'}),
            'nacionalidad': autocomplete.ModelSelect2(url='georef:nacionalidad-autocomplete'),
            'origen': autocomplete.ModelSelect2(url='georef:nacionalidad-autocomplete'),
            'destino': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }
    #Inicializacion
    def __init__(self, *args, **kwargs):
        #Obtenemos permisos
        self.base_fields['atributos'].choices = [(a.id, a.nombre) for a in TipoAtributo.objects.all()]
        self.base_fields['sintomas'].choices = [(s.id, s.nombre) for s in TipoSintoma.objects.all()]
        super(IndividuoForm, self).__init__(*args, **kwargs)

class BuscadorIndividuosForm(forms.Form):
    nombre = forms.CharField(label="Nombre", required=False)
    apellido = forms.CharField(label="Apellido", required=False)
    calle = forms.CharField(label="Calle", required=False)
    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=False,
    )
    def clean(self):
        cant = 0
        #Vemos si aportaron datos
        if self.cleaned_data['nombre']: cant+=1
        if self.cleaned_data['apellido']: cant+=1
        if self.cleaned_data['calle']: cant+=1
        if self.cleaned_data['localidad']: cant+=1
        #Exigimos al menos 2 datos
        if cant < 2:
            raise forms.ValidationError("Debe ingresar al menos dos datos.")
        else:
            return self.cleaned_data

class SearchVehiculoForm(forms.Form):
    identificacion = forms.CharField(label="Patente/Identificacion", required=True)

class SearchIndividuoForm(forms.Form):
    num_doc = forms.CharField(label="Documento/Pasaporte", required=True)

class DomicilioForm(forms.ModelForm):
    class Meta:
        model = Domicilio
        fields= '__all__'
        exclude = ('individuo', 'fecha')
        widgets = {
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class SituacionForm(forms.ModelForm):
    class Meta:
        model = Situacion
        fields= '__all__'
        exclude = ('individuo', 'fecha' )

class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields= '__all__'
        exclude = ('individuo', 'fecha')

class RelacionForm(forms.ModelForm):
    class Meta:
        model = Relacion
        fields= '__all__'
        exclude = ('individuo', 'fecha')
        widgets = {
            'relacionado': autocomplete.ModelSelect2(url='informacion:individuos-autocomplete'),
        }

class AtributoForm(forms.ModelForm):
    class Meta:
        model = Atributo
        fields= '__all__'
        exclude = ('individuo', 'activo', 'newtipo', )
        widgets = {
            'tipo': autocomplete.ModelSelect2(url='informacion:atributos-autocomplete'),
            'fecha': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }

class SintomaForm(forms.ModelForm):
    class Meta:
        model = Sintoma
        fields= '__all__'
        exclude = ('individuo', 'newtipo', )
        widgets = {
            'tipo': autocomplete.ModelSelect2(url='informacion:sintomas-autocomplete'),
            'fecha': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields= '__all__'
        exclude = ('individuo', 'tipo', 'habilitado')
        widgets = {
            'begda': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
            'endda': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }