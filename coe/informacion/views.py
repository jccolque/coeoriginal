#Imports Django
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from core.functions import paginador
from operadores.functions import obtener_operador
#imports de la app
from .models import Archivo
from .models import Vehiculo, Individuo, Origen
from .forms import ArchivoForm, VehiculoForm, IndividuoForm
from .forms import DomicilioForm, SintomaForm
# Create your views here.
@permission_required('operador.menu_informacion')
def menu(request):
    return render(request, 'menu_informacion.html', {})

#ARCHIVOS
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

@permission_required('operador.procesar_archivos')
def procesar_archivos(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id)
    archivo.procesado = not archivo.procesado
    archivo.save()
    return redirect('informacion:ver_archivo', archivo_id=archivo.id)

#VEHICULOS
@permission_required('operador.ver_vehiculo')
def listar_vehiculos(request):
    vehiculos = Vehiculo.objects.all()
    vehiculos = paginador(request, vehiculos)
    return render(request, "lista_vehiculos.html", {'vehiculos': vehiculos, })

@permission_required('operador.ver_vehiculo')
def ver_vehiculo(request, vehiculo_id):
    vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    return render(request, "ver_vehiculo.html", {'vehiculo': vehiculo, })

@permission_required('operador.cargar_vehiculo')
def cargar_vehiculo(request):
    form = VehiculoForm()
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            operador = obtener_operador(request)
            vehiculo = form.save(commit=False)
            vehiculo.operador = operador
            vehiculo.save()
            return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Vehiculo", 'form': form, 'boton': "Cargar", })

#INDIVIDUOS
@permission_required('operador.ver_individuo')
def listar_individuos(request):
    individuos = Individuo.objects.all()
    individuos = paginador(request, individuos)
    return render(request, "lista_individuos.html", {'individuos': individuos, })

@permission_required('operador.ver_individuo')
def ver_individuo(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    return render(request, "ver_individuo.html", {'individuo': individuo, })

@permission_required('operador.cargar_individuo')
def cargar_individuo(request, vehiculo_id=None):
    form = IndividuoForm()
    if request.method == "POST":
        form = IndividuoForm(request.POST)
        if form.is_valid():
            operador = obtener_operador(request)
            individuo = form.save(commit=False)
            individuo.operador = operador
            individuo.save()
            if vehiculo_id:
                vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
                origen = Origen(vehiculo=vehiculo, individuo=individuo)
                origen.save()
                return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Individuo", 'form': form, 'boton': "Cargar", })

@permission_required('operador.cargar_individuo')
def cargar_domicilio(request, individuo_id):
    form = DomicilioForm()
    if request.method == "POST":
        form = DomicilioForm(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            domicilio = form.save(commit=False)
            domicilio.individuo = individuo
            domicilio.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Domicilio", 'form': form, 'boton': "Cargar", })

@permission_required('operador.cargar_individuo')
def cargar_sintoma(request, individuo_id):
    form = SintomaForm()
    if request.method == "POST":
        form = SintomaForm(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            sintoma = form.save(commit=False)
            sintoma.individuo = individuo
            sintoma.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Domicilio", 'form': form, 'boton': "Cargar", })
