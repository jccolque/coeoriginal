#Imports django
#from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports de la app
from .models import Individuo

#Definimos nuestros autocompletes
class IndividuosTrackeadosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = []
        if self.q:
            if len(self.q) > 3:
                qs = Individuo.objects.filter(geoposiciones__tipo='ST').distinct()
        return qs