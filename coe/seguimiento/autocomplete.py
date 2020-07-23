#Imports django
from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports del proyecto
from informacion.models import Individuo
#Imports de la app
from .models import Vigia
from .functions import obtener_bajo_seguimiento

#Definimos nuestros autocompletes
class VigiasAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = []
        if self.q:
            qs = Vigia.objects.filter(operador__apellidos__icontains=self.q)
        return qs

class IndividuosVigiladosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Individuo.objects.all()
        #qs = qs.filter(vigiladores=None)
        if len(self.q) > 4:
            qs = qs.filter(Q(apellidos__icontains=self.q) | Q(num_doc__icontains=self.q))
            qs = qs.distinct()
        return qs

