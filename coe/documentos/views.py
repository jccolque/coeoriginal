#Imports Django
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from core.forms import SearchForm
from operadores.functions import obtener_operador
#Imports app
#from .models import Documento

# Create your views here.
@permission_required('operadores.menu_inventario')
def menu(request):
    return render(request, 'menu_inventario.html', {})

#ITEMS:
@permission_required('operadores.ver_item')
def lista_general(request, ):
    #documentos = Documento.objects.all()
    return render(request, 'lista_documentos.html', {'documentos': documentos, })