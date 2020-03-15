#Imports Django
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

# Create your views here.
@permission_required('informacion.menu')
def menu(request):
    return render(request, 'menu_informacion.html', {})