#Imports django
from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports del proyecto
from informacion.models import Individuo
#Imports de la app
from .models import Vigia

#Definimos nuestros autocompletes
class IndividuosVigiladosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = []
        if self.q:
            qs = Individuo.objects.filter(
                situacion__actual__conducta__in=('D','E')
            ).filter(
                Q(apellidos__icontains=self.q) |
                Q(num_doc__icontains=self.q)
            ).distinct()
        return qs

class VigiasAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = []
        if self.q:
            qs = Vigia.objects.filter(operador__apellidos__icontains=self.q)
        return qs