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
from .forms import DocumentoForm, VersionForm

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
def cargar_documento(request):
    form = DocumentoForm()
    if request.method == 'POST':
        form = DocumentoForm(request.POST)
        if form.is_valid():
            documento = form.save()
            return redirect('documentos:ver_documento', documento_id=documento.id)
    return render(request, "cargar_documento.html", {'titulo': "Cargar Documento", 'form': form, 'boton': "Agregar", })

@staff_member_required
def cargar_actualizacion(request, documento_id):
    documento = Documento.objects.get(pk=documento_id)
    operador = obtener_operador(request)
    form = VersionForm(initial={
        'documento': documento,
        'operador': operador}
    )
    if request.method == "POST":
        form = VersionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('documentos:ver_documento', documento_id=documento.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Archivo", 'form': form, 'boton': "Agregar", })

@staff_member_required
def ver_documento(request, documento_id):
    documento = Documento.objects.get(pk=documento_id)
    return render(request, "ver_documento.html", {'documento': documento, })