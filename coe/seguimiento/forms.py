#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
from informacion.models import Individuo
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
from georef.models import Localidad
#Imports de la app
from .models import Seguimiento, Vigia
from .models import OperativoVehicular, TestOperativo
from .models import Condicion
from .functions import obtener_bajo_seguimiento
from .choices import obtener_seguimientos
from .models import DatosGis

#Definimos nuestros forms aqui:
class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields= '__all__'
        exclude = ('individuo', 'atendido', 'operador')
        widgets = {
            'fecha': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        instance = kwargs.get('instance')
        super(SeguimientoForm, self).__init__(*args, **kwargs)
        if instance:
            self.fields['tipo'].choices = [(instance.tipo, instance.get_tipo_display()), ]
        else:
            self.fields['tipo'].choices = obtener_seguimientos(user)


class CondicionForm(forms.ModelForm):
    class Meta:
        model = Condicion
        fields= '__all__'
        exclude = ('individuo', 'fecha', 'atendido', 'operador')

class AtenderForm(forms.ModelForm):
    class Meta:
        model = Condicion
        fields= ('aclaracion', )

class NuevoVigia(forms.ModelForm):
    class Meta:
        model = Vigia
        fields= '__all__'
        exclude = ('controlados', )
        widgets = {
            'operador': autocomplete.ModelSelect2(url='operadores:operadores-autocomplete'),
        }

class NuevoIndividuo(forms.Form):
    individuo = forms.ModelChoiceField(
        queryset= Individuo.objects.all(),
        required= True,
        widget= autocomplete.ModelSelect2(url='seguimiento:individuosvigilados-autocomplete'),
    )

class AsignarVigia(forms.Form):
    vigia = forms.ModelChoiceField(
        queryset=Vigia.objects.all(),
        required=True,
        widget= autocomplete.ModelSelect2(url='seguimiento:vigias-autocomplete'),
    )

class OperativoForm(forms.ModelForm):
    class Meta:
        model = OperativoVehicular
        fields= '__all__'
        exclude = ('fecha_inicio', 'fecha_final', 'cazadores', 'estado')
        widgets = {
            'vehiculo': autocomplete.ModelSelect2(url='informacion:vehiculos-operativo-autocomplete'),
        }

class TestOperativoForm(forms.ModelForm):
    class Meta:
        model = OperativoVehicular
        fields= '__all__'
        exclude = ('operativo', 'individuo', 'geoposicion', 'fecha')

class DatosGisForm(forms.ModelForm):
    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=False,
    )
    class Meta:
        model = DatosGis
        fields = '__all__'
        exclude = ('operador',)
        widgets = {            
            'turno': forms.Select(attrs={'placeholder': 'SELECCIONE TURNO'}),            
            'confirmados': forms.TextInput(attrs={'placeholder': 'CANTIDAD CONFIRMADOS'}),
            'recuperados': forms.TextInput(attrs={'placeholder': 'CANTIDAD RECUPERADOS'}),
            'fallecidos': forms.TextInput(attrs={'placeholder': 'CANTIDAD FALLECIDOS'}),            
            'pcr': forms.TextInput(attrs={'placeholder': 'CANTIDAD PCR'}),
            'fecha_carga': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'},),    
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class':'form-control'
            })
        self.fields['localidad'].empty_label = "Seleccione Localidad"
        self.fields['turno'].empty_label = "Seleccione Turno"
       
        