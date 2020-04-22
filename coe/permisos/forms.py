#Imports Python
#Imports Django
from django import forms
from django.utils import timezone
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
from informacion.models import Individuo
#Imports de la app
from .choices import TIPO_PERMISO
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
    #def clean_fecha_llegada(self):
    #    fecha_llegada = self.cleaned_data["fecha_llegada"]
    #    if fecha_llegada < timezone.now():
    #        raise forms.ValidationError("La fecha de llegada debe ser posterior este momento.")
    #    else:
    #        return self.cleaned_data


class IngresanteForm(forms.ModelForm):
    class Meta:
        model = Individuo
        fields= ('num_doc', 'apellidos', 'nombres', 'sexo', 'fecha_nacimiento', 'nacionalidad', 'telefono', 'email')
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