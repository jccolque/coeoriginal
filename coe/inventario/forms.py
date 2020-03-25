#Imports Python
from datetime import date
#Imports Django
from django.utils import timezone
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
#Imports extra
from dal import autocomplete
from tinymce.widgets import TinyMCE
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
        widgets = {
            'subgrupo': autocomplete.ModelSelect2(url='inventario:subgrupos-autocomplete'),
            'responsable' : autocomplete.ModelSelect2(url='operadores:operadores-autocomplete'),
        }

class ModItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields= '__all__'
        widgets = {
            'subgrupo': autocomplete.ModelSelect2(url='inventario:subgrupos-autocomplete'),
            'responsable' : autocomplete.ModelSelect2(url='operadores:operadores-autocomplete'),
        }

class EventoItemForm(forms.ModelForm):
    class Meta:
        model = EventoItem
        fields= '__all__'
        exclude = ('fecha', )
        widgets = {
            'tarea' : autocomplete.ModelSelect2(url='tareas:tareas-autocomplete'),
            'operador' : autocomplete.ModelSelect2(url='operadores:operadores-autocomplete'),
            'item': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class TransferirForm(forms.Form):
    destino = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        widget=autocomplete.ModelSelect2(url='inventario:items-autocomplete'),
        required=True,
    )
    cantidad = forms.IntegerField()
    actuante = forms.CharField()
    detalle = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))