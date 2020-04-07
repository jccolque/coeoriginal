#Imports django
from django.db.models import Q
from django.contrib.auth.models import User
#Imports Extras
from dal import autocomplete
#Imports de la app
from .models import Rubro, SubGrupo, Item

class RubrosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Rubro.objects.all()
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs

class SubgruposAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SubGrupo.objects.all()

        rubro = self.forwarded.get('rubro', None)
        if rubro:
            qs = qs.filter(rubro=rubro)

        if self.q:
            qs = qs.filter(
                Q(nombre__icontains=self.q) |
                Q(rubro__nombre__icontains=self.q)
            )
        return qs

class ItemsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Item.objects.all()
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs