#Imports Django
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
#Imports del proyecto
from core.forms import SearchForm
from operadores.functions import obtener_operador
#Imports app
from .models import Documento
from .forms import DocumentoForm

# Create your views here.
@staff_member_required
def menu(request):
    return render(request, 'menu_documentos.html', {})

#ITEMS:
@staff_member_required
def lista_general(request, subcomite_id=None):
    documentos = Documento.objects.all()
    if subcomite_id:
        documentos = documentos.filter(subcomite__id=subcomite_id)
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            documentos = documentos.filter(nombre__icontains=search)
    return render(request, 'lista_documentos.html', {'documentos': documentos, })

@staff_member_required
def cargar_documento(request, documento_id):
    form = DocumentoForm()
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Documento", 'form': form, 'boton': "Agregar", })