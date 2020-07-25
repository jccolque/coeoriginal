#Imports django
from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports de la app
from .models import Individuo, Vehiculo

#Definimos nuestros autocompletes
class IndividuosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Individuo.objects.all()
        #qs = qs.filter(vigiladores=None)
        if len(self.q) > 4:
            qs = qs.filter(Q(apellidos__icontains=self.q) | Q(num_doc__icontains=self.q))
            qs = qs.distinct()
        return qs

#Definimos nuestros autocompletes
class VehiculosOperativoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Vehiculo.objects.filter(tipo=9)
        if self.q:
            qs = qs.filter(identificacion__icontains=self.q)
        return qs