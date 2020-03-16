#Imports Django
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from core.functions import paginador
from operadores.functions import obtener_operador
#imports de la app
from .models import Archivo
from .forms import ArchivoForm
# Create your views here.
@permission_required('operador.menu_informacion')
def menu(request):
    return render(request, 'menu_informacion.html', {})

@permission_required('operador.archivos_pendientes')
def archivos_pendientes(request):
    archivos = Archivo.objects.filter(procesado=False)
    archivos = paginador(request, archivos)
    return render(request, 'archivos_pendientes.html', {'archivos': archivos,})

@permission_required('operador.ver_archivos')
def ver_archivo(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id)
    return render(request, 'ver_archivo.html', {'archivo': archivo,})

@permission_required('operador.subir_archivos')
def subir_archivos(request):
    form = ArchivoForm()
    if request.method == "POST":
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Subir Archivo para Carga", 'form': form, 'boton': "Subir", })