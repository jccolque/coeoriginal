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
from core.api import org_id_from_name
#Imports de la app
from .models import Operador

#Definimos nuestros forms
class OperadorForm(forms.ModelForm):
    organismo = forms.CharField(label='organismo', max_length=100, widget=autocomplete.ListSelect2(url='core:organismos-autocomplete'))
    username = forms.CharField(label='Usuario', max_length=15, min_length=6)
    nombre = forms.CharField(label='Nombre', max_length=50)
    apellido = forms.CharField(label='Apellido', max_length=50)
    email = forms.EmailField(label='Email', max_length=50)
    permisos = forms.MultipleChoiceField(
        label='Permisos',
        widget=CheckboxSelectMultiple(attrs={'class':'multiplechoice',}), 
    )
    class Meta:
        model = Operador
        fields= '__all__'
        exclude = ('qrpath', 'usuario',)
    #Inicializacion
    def __init__(self, *args, **kwargs):
        permisos_list = kwargs.pop('permisos_list', None)
        if permisos_list:
            self.base_fields['permisos'].choices = permisos_list.values_list('id', 'name')
        super(OperadorForm, self).__init__(*args, **kwargs)
    #Chequeos de Seguridad
    def clean_organismo(self):
        try:
            org_name = self.cleaned_data['organismo']
            print(org_name)
            return org_id_from_name(org_name)
        except Exception as errors:
            raise forms.ValidationError(errors)
    def clean_username(self):
        if not hasattr(self, 'instance') and User.objects.filter(username=self.cleaned_data['username']):
            raise forms.ValidationError("El usuario indicado ya esta en uso, si el usuario tiene mas de una funcion, contacte al administrador")
        return self.cleaned_data['username']
    def clean_email(self):
        if not hasattr(self, 'instance') and User.objects.filter(email=self.cleaned_data['email']):
            raise forms.ValidationError("El mail indicado ya esta en uso, si el usuario tiene mas de una funcion, contacte al administrador")
        return self.cleaned_data['email']

class ModPassword(forms.Form):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'readonly':'readonly'}))
    passwd1 = forms.CharField(label="Password", max_length=32, widget=forms.PasswordInput)
    passwd2 = forms.CharField(label="Repetir Password", max_length=32, widget=forms.PasswordInput)
    def clean_passwd2(self):
        passwd1 = self.cleaned_data['passwd1']
        passwd2 = self.cleaned_data['passwd2']
        if passwd1 != passwd2:
            raise forms.ValidationError("Las contraseñas no son iguales")
        return ''

class AuditoriaForm(forms.Form):
    usuario = forms.ModelChoiceField(
        label='Usuario',
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url='core:usuarios-autocomplete'),
        required=True)
    begda = forms.DateField(label='Inicio', initial=timezone.now(), widget=forms.SelectDateWidget())
    endda = forms.DateField(label='Fin',initial=timezone.now(), widget=forms.SelectDateWidget())
    def __init__(self, *args, **kwargs):
        super(AuditoriaForm, self).__init__(*args, **kwargs)
        if kwargs.get('initial', None):
            if kwargs['initial'].get('usuario'):
                self.fields['usuario'].widget = forms.HiddenInput()
    def clean(self):
        if self.cleaned_data['begda'] > self.cleaned_data['endda']:
            raise forms.ValidationError("La fecha de Inicio debe ser Menor a la de fin.")
        if self.cleaned_data['endda'] > date.today():
            raise forms.ValidationError("No puede ingresar una fecha posteriores a hoy.")
        return self.cleaned_data

class AsistenciaForm(forms.Form):
    num_doc = forms.IntegerField(label='Num de Documento', required=False)
    widgets = {
        'num_doc': forms.TextInput(attrs={}),
    }
    def clean(self):
        #Buscamos si existe el operador
        try:           
            if self.cleaned_data['num_doc']:
                operador = Operador.objects.get(num_doc=self.cleaned_data['num_doc'])
        except Operador.DoesNotExist:
            raise forms.ValidationError('No existe Operador Autorizado con ese Documento de Identidad.')
        #Lo preparamos para futuro uso
        if operador:
            self.operador = operador
        return self.cleaned_data   
