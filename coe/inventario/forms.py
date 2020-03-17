#Imports Python
from datetime import date
#Imports Django
from django.utils import timezone
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
#Imports extra
from dal import autocomplete
#Imports del proyecto
#Imports de la app
from .models import Item, EventoItem

#Definimos nuestros forms
class ItemForm(forms.ModelForm):
    actuante = forms.CharField(label='actuante', max_length=100, required=True)
    cantidad = forms.IntegerField(required=True)
    #agregar grupo y listfilter
    class Meta:
        model = Item
        fields= '__all__'

class EventoItemForm(forms.ModelForm):
    class Meta:
        model = EventoItem
        fields= '__all__'
        exclude = ('fecha', )
    widgets = {
        'item': forms.TextInput(attrs={'readonly': 'readonly'}),
    }