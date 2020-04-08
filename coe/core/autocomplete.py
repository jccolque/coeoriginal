#Imports django
from django.core.cache import cache
from django.contrib.auth.models import User
#Imports Extras
from dal import autocomplete
#Imports de la app
from core.api import obtener_organismos

class UsuariosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all()
        if self.q:
            qs = qs.filter(username__istartswith=self.q)
        return qs

class OrganismosAutocomplete(autocomplete.Select2ListView):
    def get_list(self):
        return [o[1] for o in obtener_organismos()]