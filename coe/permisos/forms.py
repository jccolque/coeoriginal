#Imports Python
#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
from informacion.models import Individuo
#Imports de la app
from .models import Permiso, IngresoProvincia

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

class IngresoProvinciaForm(forms.ModelForm):
    class Meta:
        model = IngresoProvincia
        fields= '__all__'
        exclude = ('fecha', 'token', 'individuos', 'estado', 'plan_vuelo', 'dut')
        widgets = {
            'fecha_llegada': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}, ),
            'origen': autocomplete.ModelSelect2(url='georef:provincia-autocomplete'),
            'destino': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class IngresanteForm(forms.ModelForm):
    class Meta:
        model = Individuo
        fields= ('num_doc', 'apellidos', 'nombres', 'sexo', 'fecha_nacimiento', 'nacionalidad', 'telefono', 'email')
        widgets = {
            'fecha_nacimiento': XDSoftDatePickerInput(attrs={'autocomplete':'off'}),
            'nacionalidad': autocomplete.ModelSelect2(url='georef:nacionalidad-autocomplete'),
        }

class DUTForm(forms.ModelForm):
    class Meta:
        model = IngresoProvincia
        fields= ('dut',)

class PlanVueloForm(forms.ModelForm):
    class Meta:
        model = IngresoProvincia
        fields= ('plan_vuelo',)