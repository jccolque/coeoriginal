#Imports django
from django.contrib.auth.models import User
#Imports Extras
from dal import autocomplete

class UsuariosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all()
        if self.q:
            qs = qs.filter(username__istartswith=self.q)
        return qs