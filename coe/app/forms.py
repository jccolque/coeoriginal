#Imports Django
from django import forms
#Imports extra
from fcm_django.models import FCMDevice
from dal import autocomplete
#Imports de la app
from .choices import TIPO_ICONO
from .models import AppNotificacion

#Definimos nuestros forms aqui:
class AppNotificacionForm(forms.ModelForm):
    class Meta:
        model = AppNotificacion
        fields= '__all__'
        exclude = ('fecha', )
        widgets = {
            'appdata': autocomplete.ModelSelect2(url='app:appdata-autocomplete'),
        }

class SendNotificationForm(forms.Form):
    dispositivo = forms.ModelChoiceField(queryset=FCMDevice.objects.all(), widget=autocomplete.ModelSelect2(url='app:dispositivo-autocomplete'))
    titulo = forms.CharField(label="Titulo", required=True)
    texto = forms.CharField(label="Texto", widget=forms.Textarea())
    icono = forms.ChoiceField(choices=TIPO_ICONO, required=True)
    color = forms.CharField(max_length=9, initial="#FFFFFF", widget=forms.TextInput(attrs={'type': 'color'}))