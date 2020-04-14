#Imports django
from django.db.models import Q
#Imports Extras
from dal import autocomplete
from fcm_django.models import FCMDevice
#Imports de la app
from .models import Individuo, AppData

#Definimos nuestros autocompletes
class IndividuosAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = []
        if self.q:
            if len(self.q) > 3:
                qs = Individuo.objects.filter(
                    Q(apellidos__icontains=self.q) |
                    Q(num_doc__icontains=self.q)
                )
        return qs

class AppDataAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = AppData.objects.all()
        if self.q:
            qs = qs.filter(
                Q(individuo__apellidos__icontains=self.q) |
                Q(individuo__num_doc__icontains=self.q)
            )
        return qs

class DispositivoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = FCMDevice.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs