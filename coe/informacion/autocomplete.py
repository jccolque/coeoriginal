#Imports django
from django.contrib.auth.models import User
from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports de la app
from .models import TipoSintoma, TipoAtributo

class SintomaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TipoSintoma.objects.all()
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs

class AtributoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TipoAtributo.objects.all()
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs