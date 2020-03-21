#Imports de Django
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
#Impors de la app

# Create your views here.
@permission_required('operadores.menu_inscripciones')
def menu(request):
    return render(request, 'menu_inscripciones.html', {})