#Imports Django
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
#Imports del proyecto

# Create your views here.
@permission_required('operadores.tablero_jerarquico')
def menu(request):
    return render(request, 'menu_tablero.html', {})