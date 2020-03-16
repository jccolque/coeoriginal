#Imports django
from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports de la app
from .models import Departamento, Localidad, Barrio

class DepartamentoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Departamento.objects.all()
        if self.q:
            qs = qs.filter(istartswith=self.q)
        return qs

class LocalidadAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Localidad.objects.all()

        departamento = self.forwarded.get('departamento', None)
        if departamento:
            qs = qs.filter(departamento=departamento)

        if self.q:
            qs = qs.filter(nombre__istartswith=self.q)
        return qs

class BarrioAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Barrio.objects.all()
        
        localidad = self.forwarded.get('localidad', None)
        if localidad:
            qs = qs.filter(localidad=localidad)
        
        if self.q:
            qs = qs.filter(nombre__istartswith=self.q)
        return qs