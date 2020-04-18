#Imports django
from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports del proyecto
from informacion.models import Individuo
#Imports de la app
from .models import GeOperador

#Definimos nuestros autocompletes
class IndividuosTrackeadosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = []
        if self.q:
            qs = Individuo.objects.filter(
                geoposiciones__tipo='ST'
            ).filter(
                Q(apellidos__icontains=self.q) |
                Q(num_doc__icontains=self.q)
            ).distinct()
        return qs

class GeOperadoresAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = []
        if self.q:
            qs = GeOperador.objects.filter(operador__apellidos__icontains=self.q)
        return qs