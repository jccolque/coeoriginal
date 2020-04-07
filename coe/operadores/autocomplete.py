#Imports django
from django.contrib.auth.models import User
from django.db.models import Q
#Imports Extras
from dal import autocomplete
#Imports de la app
from .models import Operador, SubComite

class SubComiteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SubComite.objects.all()
        if self.q:
            qs = qs.filter(nombre__icontains=self.q)
        return qs

class UsuariosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all()
        if self.q:
            qs = qs.filter(username__istartswith=self.q)
        return qs

class OperadoresAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Operador.objects.all()
        if self.q:
            qs = qs.filter(
                Q(apellidos__icontains=self.q) |
                Q(nombres__icontains=self.q)
            )
        return qs