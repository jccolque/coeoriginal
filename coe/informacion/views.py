import csv
#Imports Django
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from core.functions import paginador
from core.forms import SearchForm
from operadores.functions import obtener_operador
#imports de la app
from .models import Archivo
from .models import Vehiculo, Individuo, Origen
from .models import TipoAtributo, TipoSintoma
from .forms import ArchivoForm, VehiculoForm, IndividuoForm
from .forms import DomicilioForm, AtributoForm, SintomaForm
from .forms import SearchIndividuoForm

# Create your views here.
@permission_required('operadores.menu_informacion')
def menu(request):
    return render(request, 'menu_informacion.html', {})

#ARCHIVOS
@permission_required('operadores.archivos_pendientes')
def archivos_pendientes(request):
    archivos = Archivo.objects.filter(procesado=False)
    archivos = paginador(request, archivos)
    return render(request, 'archivos_pendientes.html', {'archivos': archivos,})

@permission_required('operadores.ver_archivos')
def ver_archivo(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id)
    return render(request, 'ver_archivo.html', {'archivo': archivo,})

@permission_required('operadores.subir_archivos')
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

@permission_required('operadores.procesar_archivos')
def procesar_archivos(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id)
    archivo.procesado = not archivo.procesado
    archivo.save()
    return redirect('informacion:ver_archivo', archivo_id=archivo.id)

#VEHICULOS
@permission_required('operadores.ver_individuo')
def buscar_vehiculo(request):
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            try:
                vehiculo = Vehiculo.objects.get(identificacion=search)
                return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
            except:
                form.add_error('search', "No se Encontro Vehiculo con esa identificacion.")
    return render(request, "extras/generic_form.html", {'titulo': "Buscar Vehiculo", 'form': form, 'boton': "Buscar", })

@permission_required('operadores.ver_vehiculo')
def listar_vehiculos(request, tipo_id=None):
    vehiculos = Vehiculo.objects.all()
    if tipo_id:
        vehiculos = vehiculos.filter(tipo=tipo_id)
    vehiculos = paginador(request, vehiculos)
    return render(request, "lista_vehiculos.html", {'vehiculos': vehiculos, })

@permission_required('operadores.ver_vehiculo')
def ver_vehiculo(request, vehiculo_id):
    vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    return render(request, "ver_vehiculo.html", {'vehiculo': vehiculo, })

@permission_required('operadores.cargar_vehiculo')
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
@permission_required('operadores.ver_individuo')
def buscar_individuo(request):
    form = SearchIndividuoForm()
    if request.method == "POST":
        form = SearchIndividuoForm(request.POST)
        if form.is_valid():
            individuos = Individuo.objects.all()
            apellidos = form.cleaned_data['apellidos']
            if apellidos:
                individuos = Individuo.objects.filter(apellidos__icontains=apellidos)
            num_doc = form.cleaned_data['num_doc']
            if num_doc:
                individuos = Individuo.objects.filter(num_doc=num_doc)
            return render(request, "lista_individuos.html", {'individuos': individuos, })
    return render(request, "extras/generic_form.html", {'titulo': "Buscar Individuo", 'form': form, 'boton': "Buscar", })

@permission_required('operadores.ver_individuo')
def listar_individuos(request):
    individuos = Individuo.objects.all()
    individuos = paginador(request, individuos)
    return render(request, "lista_individuos.html", {'individuos': individuos, })

@permission_required('operadores.ver_individuo')
def ver_individuo(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    return render(request, "ver_individuo.html", {'individuo': individuo, })

@permission_required('operadores.cargar_individuo')
def cargar_individuo(request, vehiculo_id=None, individuo_id=None):
    individuo = None
    if individuo_id:#Si manda individuo es para modificar
        individuo = Individuo.objects.get(pk=individuo_id)
    form = IndividuoForm(instance=individuo)
    if request.method == "POST":
        form = IndividuoForm(request.POST, instance=individuo)
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

@permission_required('operadores.cargar_individuo')
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

@permission_required('operadores.cargar_individuo')
def cargar_atributo(request, individuo_id):
    form = AtributoForm()
    if request.method == "POST":
        form = AtributoForm(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            sintoma = form.save(commit=False)
            sintoma.individuo = individuo
            sintoma.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Atributo", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.cargar_individuo')
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
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Sintoma", 'form': form, 'boton': "Cargar", })

#Reportes en el sistema
@permission_required('operadores.reportes')
def reporte_basico(request):
    atributos = TipoAtributo.objects.all()
    sintomas = TipoSintoma.objects.all()
    if request.method == "POST":
        print(request.POST)
    return render(request, "reporte_basico.html", {'atributos': atributos, 'sintomas': sintomas, })

@permission_required('operadores.reportes')
def csv_individuos(request):
    individuos = Individuo.objects.all()
    individuos = individuos.prefetch_related('atributos', 'sintomas')
    #Iniciamos la creacion del csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="individuos.csv"'
    writer = csv.writer(response)
    writer.writerow(['REPORTE DE INDIVIDUOS'])
    writer.writerow(['TIPO DOC', 'NUM DOC', 'APELLIDO', 'NOMBRE', 'NACIONALIDAD', 'ORIGEN', 'DESTINO LOCAL', 'OBSERVACIONES', 'ATRIBUTOS','SINTOMAS'])
    for individuo in individuos:
        writer.writerow([
            individuo.get_tipo_doc_display(),
            individuo.num_doc,
            individuo.apellidos,
            individuo.nombres,
            individuo.nacionalidad.nombre,
            str(individuo.origen),
            str(individuo.destino),
            individuo.observaciones,
            str([a.tipo.nombre for a in individuo.atributos.all()]),
            str([s.tipo.nombre for s in individuo.sintomas.all()]),
        ])
    #Enviamos el archivo para descargar
    return response