#Imports Python
from datetime import date
#Imports Django
from django.utils import timezone
from django import forms
from django.contrib.auth.models import User
#Imports extra
from dal import autocomplete
from tinymce.widgets import TinyMCE
#Imports del proyecto
from coe.settings import SECRET_KEY
from core.widgets import XDSoftDatePickerInput, XDSoftDateTimePickerInput
#Imports de la app
from .models import Aclaracion

#Definimos nuestros formularios
class SearchForm(forms.Form):
    search = forms.CharField(label="", required=True)

class UploadCsv(forms.Form):
    csvfile = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))

class UploadFoto(forms.Form):
    imagen = forms.FileField()

class UploadCsvWithPass(forms.Form):
    csvfile = forms.FileField(label="Archivo CSV Masivo", widget=forms.FileInput(attrs={'accept': ".csv"}))
    passwd = forms.CharField(label="Password de Administrador", max_length=100, widget=forms.PasswordInput)
    def clean(self):
        if self.cleaned_data['passwd'] == SECRET_KEY:
            return self.cleaned_data
        else:
            raise forms.ValidationError("La contraseña ingresada es incorrecta.")

class UploadDobleCsvWithPass(forms.Form):
    csvfile1 = forms.FileField(label="Archivo CSV Masivo", widget=forms.FileInput(attrs={'accept': ".csv"}))
    csvfile2 = forms.FileField(label="Archivo CSV Secundario", widget=forms.FileInput(attrs={'accept': ".csv"}))
    passwd = forms.CharField(label="Password de Administrador", max_length=100, widget=forms.PasswordInput)
    def clean(self):
        if self.cleaned_data['passwd'] == SECRET_KEY:
            return self.cleaned_data
        else:
            raise forms.ValidationError("La contraseña ingresada es incorrecta.")

class MesForm(forms.Form):
    month = forms.ChoiceField(label='Periodo', choices=[(m,m) for m in range(1,13)], initial=timezone.now().month)
    year = forms.ChoiceField(label='Año', choices=[(y,y) for y in range(2020, timezone.now().year+1)], initial=timezone.now().year)
    def __init__(self, *args, **kwargs):
        self.alinear = [('month', 'year'), ]
        super(MesForm, self).__init__(*args, **kwargs)

class FechaForm(forms.Form):
    fecha = forms.DateField(initial=date.today(), widget=forms.SelectDateWidget())

class PeriodoForm(forms.Form):
    begda = forms.DateField(label='Inicio', initial=timezone.now(), widget=forms.SelectDateWidget())
    endda = forms.DateField(label='Fin',initial=timezone.now(), widget=forms.SelectDateWidget())
    def clean(self):
        if self.cleaned_data['begda'] > self.cleaned_data['endda']:
            raise forms.ValidationError("La fecha de Inicio debe ser Menor a la de fin.")
        self.begda = self.cleaned_data['begda']
        self.endda = self.cleaned_data['endda']
        return self.cleaned_data

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

class EmailForm(forms.Form):
    destinatario = forms.EmailField(label='Correo Destinatario', required=True)
    asunto = forms.CharField(label="Asunto", required=True)
    cuerpo = forms.CharField(label="Cuerpo", widget=forms.Textarea(), required=True)
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        if kwargs.get('initial', None):
            self.fields['destinatario'].widget.attrs['readonly'] = True

class JustificarForm(forms.Form):
    justificacion = forms.CharField(widget=forms.Textarea())

class AclaracionForm(forms.Form):
    class Meta:
        model = Aclaracion
        fields= '__all__'
        exclude = ('operador', )
        widgets = {
            'fecha': XDSoftDateTimePickerInput(attrs={'autocomplete':'off'}),
        }