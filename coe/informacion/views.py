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
from .choices import TIPO_ESTADO, TIPO_CONDUCTA
from .models import Archivo
from .models import Vehiculo, Individuo, Origen
from .models import Domicilio, Atributo, Sintoma
from .models import TipoAtributo, TipoSintoma
from .forms import ArchivoForm, VehiculoForm, IndividuoForm
from .forms import DomicilioForm, AtributoForm, SintomaForm
from .forms import SituacionForm
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
    if individuo_id:#Si manda individuo es para modificar
        individuo = Individuo.objects.get(pk=individuo_id)
        domicilio_actual = individuo.domicilio_actual()
        form = IndividuoForm(
            instance=individuo,
            initial={
                'dom_localidad': domicilio_actual.localidad,
                'dom_calle': domicilio_actual.calle,
                'dom_numero': domicilio_actual.numero,
                'dom_aclaracion': domicilio_actual.aclaracion,
                'atributos': [a.tipo.id for a in individuo.atributos.all()],
                'sintomas': [s.tipo.id for s in individuo.sintomas.all()],
            }
        )
    else:
        form = IndividuoForm()
    #Analizamos si mando informacion:
    if request.method == "POST":
        form = IndividuoForm(request.POST, instance=individuo)
        if form.is_valid():
            operador = obtener_operador(request)
            individuo = form.save(commit=False)
            individuo.operador = operador
            individuo.save()
            #Generamos modelos externos:
            #Creamos domicilio
            domicilio = Domicilio()
            domicilio.individuo = individuo
            domicilio.localidad = form.cleaned_data['dom_localidad']
            domicilio.calle = form.cleaned_data['dom_calle']
            domicilio.numero = form.cleaned_data['dom_numero']
            domicilio.aclaracion = form.cleaned_data['dom_aclaracion']
            domicilio.save()
            #Creamos atributos
            atributos = form.cleaned_data['atributos']
            individuo.atributos.all().delete()
            for atributo_id in atributos:
                atributo = Atributo()
                atributo.individuo = individuo
                atributo.tipo = TipoAtributo.objects.get(pk=atributo_id)
                atributo.save()           
            #Creamos sintomas
            sintomas = form.cleaned_data['sintomas']
            individuo.sintomas.all().delete()
            for sintoma_id in sintomas:
                sintoma = Sintoma()
                sintoma.individuo = individuo
                sintoma.tipo = TipoSintoma.objects.get(pk=sintoma_id)
                sintoma.save()  
            #Si vino en un vehiculo
            if vehiculo_id:
                vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
                origen = Origen(vehiculo=vehiculo, individuo=individuo)
                origen.save()
                return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "cargar_individuo.html", {'titulo': "Cargar Individuo", 'form': form, 'boton': "Cargar", })

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
def cargar_situacion(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = SituacionForm(instance=individuo.situacion_actual())
    if request.method == "POST":
        form = SituacionForm(request.POST, initial={'individuo': individuo})
        if form.is_valid():
            form.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Situacion", 'form': form, 'boton': "Cargar", }) 

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
    #Definimos un objecto para jugar
    class Creportado(object):
        individuo = Individuo()
        atributos = 0
        sintomas = 0
    #iniciamos la vista
    estados = TIPO_ESTADO
    conductas = TIPO_CONDUCTA
    atributos = TipoAtributo.objects.all()
    sintomas = TipoSintoma.objects.all()
    if request.method == "POST":
        reportados = {}
        #Obtenemos todos los parametros
        #begda = request.POST['begda']
        #endda = request.POST['endda']
        estados = request.POST.getlist('estado')
        conductas = request.POST.getlist('conducta')
        atributos = request.POST.getlist('atributo')
        sintomas = request.POST.getlist('sintoma')
        #Obtenemos todos los individuos que esten en ese estado
        full_individuos = Individuo.objects.filter(
            situaciones__estado__in=estados,
            situaciones__conducta__in=conductas).distinct()
        for atributo in atributos:
            individuos = full_individuos.filter(atributos__tipo=atributo)
            for individuo in individuos:
                if individuo.id not in reportados:#Si no esta lo agregamos
                    reportado = Creportado()
                    reportado.individuo = individuo
                    reportados[reportado.individuo.id] = reportado
                #Le sumamos 1 a ese atributo
                reportados[individuo.id].atributos += 1
        for sintoma in sintomas:
            individuos = full_individuos.filter(sintomas__tipo=sintoma)
            for individuo in individuos:
                if individuo.id not in reportados:#Si no esta lo agregamos
                    reportado = Creportado()
                    reportado.individuo = individuo
                    reportados[reportado.individuo.id] = reportado
                #Le sumamos 1 a ese atributo
                reportados[individuo.id].sintomas += 1
        #los volvemos una lista:
        reportados = list(reportados.values())
        reportados.sort(key=lambda x: x.sintomas, reverse=True)
        return render(request, "reporte_basico_mostrar.html", {'reportados': reportados, })
    return render(request, "reporte_basico_buscar.html", {
        'estados': estados, 'conductas': conductas,
        'atributos': atributos, 'sintomas': sintomas, })

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