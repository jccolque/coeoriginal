#Imports Python
from datetime import date
#Imports Django
from django.utils import timezone
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.forms.widgets import CheckboxSelectMultiple
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.choices import TIPO_DOCUMENTOS
from georef.models import Localidad
#Imports de la app
from .models import TipoAtributo, TipoSintoma
from .models import Vehiculo, ControlVehiculo
from .models import Individuo, Domicilio, Atributo, Sintoma
from .models import Situacion, Archivo, Relacion, Seguimiento

#Definimos nuestros forms
class ArchivoForm(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['tipo', 'nombre', 'archivo', ]

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
        exclude = ('individuo', 'fecha' )

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
        }

class SintomaForm(forms.ModelForm):
    class Meta:
        model = Sintoma
        fields= '__all__'
        exclude = ('individuo', 'newtipo', )
        widgets = {
            'tipo': autocomplete.ModelSelect2(url='informacion:sintomas-autocomplete'),
        }