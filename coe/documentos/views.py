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
from .models import Documento, Version
from .forms import DocumentoForm, VersionForm
#Publico
def lista_publica(request):
    documentos = Documento.objects.filter(publico=True)
    documentos = documentos.prefetch_related('versiones')
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            documentos = documentos.filter(nombre__icontains=search)
    return render(request, 'lista_publica.html', {'documentos': documentos, })    

#Privado.
@permission_required('operadores.menu_documentos')
def menu(request):
    return render(request, 'menu_documentos.html', {})

#ITEMS:
@permission_required('operadores.menu_documentos')
def lista_general(request, subco_id=None):
    documentos = Documento.objects.all()
    if subco_id:
        documentos = documentos.filter(subcomite__id=subco_id)
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            documentos = documentos.filter(nombre__icontains=search)
    return render(request, 'lista_documentos.html', {'documentos': documentos, })

@permission_required('operadores.menu_documentos')
def cargar_documento(request):
    form = DocumentoForm()
    if request.method == 'POST':
        form = DocumentoForm(request.POST)
        if form.is_valid():
            documento = form.save()
            return redirect('documentos:ver_documento', documento_id=documento.id)
    return render(request, "cargar_documento.html", {'titulo': "Cargar Documento", 'form': form, 'boton': "Agregar", })

@permission_required('operadores.menu_documentos')
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

@permission_required('operadores.documentos')
def eliminar_version(request, version_id):
    version = Version.objects.get(pk=version_id)
    documento = version.documento
    version.delete()
    return redirect('documentos:ver_documento', documento_id=documento.id)

@permission_required('operadores.menu_documentos')
def ver_documento(request, documento_id):
    documento = Documento.objects.get(pk=documento_id)
    return render(request, "ver_documento.html", {'documento': documento, })

@permission_required('operadores.documentos')
def cambiar_estado(request, documento_id):
    documento = Documento.objects.get(pk=documento_id)
    documento.publico = not documento.publico
    documento.save()
    return redirect('documentos:ver_documento', documento_id=documento.id)

@permission_required('operadores.documentos')
def eliminar_doc(request, documento_id):
    documento = Documento.objects.get(pk=documento_id)
    documento.delete()
    return redirect('documentos:lista_general')