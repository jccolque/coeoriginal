#Imports Django
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
from informacion.models import Individuo
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
#Imports de la app
from .models import Seguimiento, Vigia
from .models import OperativoVehicular, TestOperativo
from .functions import obtener_bajo_seguimiento
from .choices import obtener_seguimientos

#Definimos nuestros forms aqui:
class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = Seguimiento
        fields= '__all__'
        exclude = ('individuo', 'operador')
        widgets = {
            'fecha': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        instance = kwargs.pop('instance')
        super(SeguimientoForm, self).__init__(*args, **kwargs)
        if instance:
            self.fields['tipo'].choices = [instance.tipo, ]
        else:
            self.fields['tipo'].choices = obtener_seguimientos(user)



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
        queryset= obtener_bajo_seguimiento(),
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
        