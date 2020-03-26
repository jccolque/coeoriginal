#Imports Python
#Imports Django
from django.utils import timezone
from django import forms
#Imports extra
from dal import autocomplete
#Imports del proyecto
from core.widgets import XDSoftDateTimePickerInput
#Imports de la app
from .models import Tarea, Responsable, EventoTarea

#Definimos nuestros forms
class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = '__all__'
        widgets = {
            'subcomite': autocomplete.ModelSelect2(url='operadores:subcomite-autocomplete'),
            'begda': XDSoftDateTimePickerInput(),
            'endda': XDSoftDateTimePickerInput(),
        }
    def clean_endda(self):
        if self.cleaned_data['begda'] > self.cleaned_data['endda']:
            raise forms.ValidationError("No se puede ingresar una fecha de inicio posterior a la de finalizacion.")
        if timezone.now() > self.cleaned_data['endda']:
            raise forms.ValidationError("No se puede ingresar una fecha de finalizacion pasada.")
        return self.cleaned_data['endda']

class ResponsableForm(forms.ModelForm):
    class Meta:
        model = Responsable
        fields = '__all__'
        exclude = ('fecha_asignacion', 'tarea')
        widgets = {
            'operador': autocomplete.ModelSelect2(url='operadores:operadores-autocomplete'),
        }

class EventoTareaForm(forms.ModelForm):
    class Meta:
        model = EventoTarea
        fields = '__all__'
        exclude = ('tarea', 'fecha', )
    def __init__(self, *args, **kwargs):
        super(EventoTareaForm, self).__init__(*args, **kwargs)
        tarea = kwargs.get('initial').get('tarea')
        self.fields['responsable'].queryset = Responsable.objects.filter(tarea=tarea)