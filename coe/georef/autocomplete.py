#Imports django
from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports de la app
from .models import Departamento, Provincia, Localidad, Barrio
from .models import Nacionalidad

class ProvinciaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Provincia.objects.all()
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs

class DepartamentoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Departamento.objects.all()
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs

class LocalidadAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Localidad.objects.all()
        departamento = self.forwarded.get('departamento', None)
        if departamento:
            qs = qs.filter(departamento=departamento)

        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs

class BarrioAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Barrio.objects.all()
        localidad = self.forwarded.get('localidad', None)
        #Si hay localidad en el form, usamos filtro:
        if localidad:
            qs = qs.filter(localidad=localidad)
        #Usamos texto
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs

class NacionalidadAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Nacionalidad.objects.all()
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs