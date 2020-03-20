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
from georef.models import Localidad
#Imports de la app
from .models import TipoAtributo, TipoSintoma
from .models import Archivo, Vehiculo
from .models import Individuo, Domicilio, Atributo, Sintoma
from .models import Situacion

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

class IndividuoForm(forms.ModelForm):
    dom_localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.all(),
        widget=autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        required=False,
    )
    dom_calle = forms.CharField(required=False, )
    dom_numero = forms.IntegerField(required=False, )
    dom_aclaracion = forms.CharField(required=False, )
    atributos = forms.MultipleChoiceField(
        choices=[(t.id, t.nombre) for t in TipoAtributo.objects.all()],
        widget=CheckboxSelectMultiple(attrs={'class':'multiplechoice',}),
        required=False
    )
    sintomas = forms.MultipleChoiceField(
        choices=[(s.id, s.nombre) for s in TipoSintoma.objects.all()],
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

class SearchIndividuoForm(forms.Form):
    num_doc = forms.CharField(required=False)
    apellidos = forms.CharField(required=False)

class DomicilioForm(forms.ModelForm):
    class Meta:
        model = Domicilio
        fields= '__all__'
        exclude = ('individuo', )
        widgets = {
            'localidad': autocomplete.ModelSelect2(url='georef:localidad-autocomplete'),
        }

class SituacionForm(forms.ModelForm):
    class Meta:
        model = Situacion
        fields= '__all__'
        exclude = ('individuo', )

class AtributoForm(forms.ModelForm):
    class Meta:
        model = Atributo
        fields= '__all__'
        exclude = ('individuo', 'activo', )
        widgets = {
            'tipo': autocomplete.ModelSelect2(url='informacion:atributos-autocomplete'),
        }

class SintomaForm(forms.ModelForm):
    class Meta:
        model = Sintoma
        fields= '__all__'
        exclude = ('individuo', )
        widgets = {
            'tipo': autocomplete.ModelSelect2(url='informacion:sintomas-autocomplete'),
        }