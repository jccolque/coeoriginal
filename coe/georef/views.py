#Import Python Standard
#Imports de Django
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from coe.settings import SECRET_KEY, GEOPOSITION_GOOGLE_MAPS_API_KEY
from core.forms import UploadCsvWithPass
from core.functions import is_related
#Imports de la app
from .models import Nacionalidad, Provincia, Departamento, Localidad, Barrio, Ubicacion
from .forms import NacionalidadForm, ProvinciaForm, DepartamentoForm
from .forms import LocalidadForm, BarrioForm, UbicacionForm

# Create your views here.
@permission_required('operadores.menu_georef')
def menu(request):
    return render(request, 'menu_georef.html', {})

#Nacionalidades
@permission_required('operadores.menu_georef')
def lista_nacionalidades(request):
    nacionalidades = Nacionalidad.objects.all()
    return render(request, 'lista_nacionalidades.html', {
        'nacionalidades': nacionalidades,
        'has_table': True,
    })

@permission_required('operadores.menu_georef')
def crear_nacionalidad(request, nacionalidad_id=None):
    nacionalidad = None
    if nacionalidad_id:
        nacionalidad = Nacionalidad.objects.get(pk=nacionalidad_id)
    form = NacionalidadForm(instance=nacionalidad)
    if request.method == "POST":
        form = NacionalidadForm(request.POST, instance=nacionalidad)
        if form.is_valid():
            form.save()
            return redirect('georef:lista_nacionalidades')
    return render(request, "extras/generic_form.html", {'titulo': "Crear Nacionalidad", 'form': form, 'boton': "Crear", })

@permission_required('operadores.menu_georef')
def delete_nacionalidad(request, nacionalidad_id):
    nacionalidad = Nacionalidad.objects.get(pk=nacionalidad_id)
    if is_related(nacionalidad):
        return render(request, 'extras/error.html', {
            'titulo': 'Eliminar Nacionalidad',
            'error': "La nacionalidad no puede ser borrada pues es Clave de Otros Registros, Contacte al Administrador.",
        })
    else:
        nacionalidad.delete()
    return redirect('georef:lista_nacionalidades')

#Provincias
@permission_required('operadores.menu_georef')
def lista_provincias(request):
    provincias = Provincia.objects.all()
    provincias = provincias.select_related('nacion')
    return render(request, 'lista_provincias.html', {
        'provincias': provincias,
        'has_table': True,
    })

@permission_required('operadores.menu_georef')
def crear_provincia(request, provincia_id=None):
    provincia = None
    if provincia_id:
        provincia = Provincia.objects.get(pk=provincia_id)
    form = ProvinciaForm(instance=provincia)
    if request.method == "POST":
        form = ProvinciaForm(request.POST, instance=provincia)
        if form.is_valid():
            form.save()
            return redirect('georef:lista_provincias')
    return render(request, "extras/generic_form.html", {'titulo': "Crear Provincia", 'form': form, 'boton': "Crear", })

@permission_required('operadores.menu_georef')
def delete_provincia(request, provincia_id):
    provincia = Provincia.objects.get(pk=provincia_id)
    if is_related(provincia):
        return render(request, 'extras/error.html', {
            'titulo': 'Eliminar Provincia',
            'error': "La Provincia no puede ser borrada pues es Clave de Otros Registros, Contacte al Administrador.",
        })
    else:
        provincia.delete()
    return redirect('georef:lista_provincias')

#Departamentos
@permission_required('operadores.menu_georef')
def lista_departamentos(request):
    departamentos = Departamento.objects.all()
    departamentos = departamentos.select_related('provincia', 'provincia__nacion')
    return render(request, 'lista_departamentos.html', {
        'departamentos': departamentos,
        'has_table': True,
    })

@permission_required('operadores.menu_georef')
def crear_departamento(request, departamento_id=None):
    departamento = None
    if departamento_id:
        departamento = Departamento.objects.get(pk=departamento_id)
    form = DepartamentoForm(instance=departamento)
    if request.method == "POST":
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            return redirect('georef:lista_departamentos')
    return render(request, "extras/generic_form.html", {'titulo': "Crear Departamento", 'form': form, 'boton': "Crear", })

@permission_required('operadores.menu_georef')
def delete_departamento(request, departamento_id):
    departamento = Departamento.objects.get(pk=departamento_id)
    if is_related(departamento):
        return render(request, 'extras/error.html', {
            'titulo': 'Eliminar Departamento',
            'error': "El Departamento no puede ser borrada pues es Clave de Otros Registros, Contacte al Administrador.",
        })
    else:
        departamento.delete()
    return redirect('georef:lista_departamentos')

#Localidad
@permission_required('operadores.menu_georef')
def lista_localidades(request):
    localidades = Localidad.objects.all()
    localidades = localidades.select_related('departamento', 'departamento__provincia', 'departamento__provincia__nacion')
    return render(request, 'lista_localidades.html', {
        'localidades': localidades,
        'has_table': True,
    })

@permission_required('operadores.menu_georef')
def crear_localidad(request, localidad_id=None):
    localidad = None
    if localidad_id:
        localidad = Localidad.objects.get(pk=localidad_id)
    form = LocalidadForm(instance=localidad)
    if request.method == "POST":
        form = LocalidadForm(request.POST, instance=localidad)
        if form.is_valid():
            form.save()
            return redirect('georef:lista_localidades')
    return render(request, "extras/generic_form.html", {'titulo': "Crear Localidad", 'form': form, 'boton': "Crear", })

@permission_required('operadores.menu_georef')
def delete_localidad(request, localidad_id):
    localidad = Localidad.objects.get(pk=localidad_id)
    if is_related(localidad):
        return render(request, 'extras/error.html', {
            'titulo': 'Eliminar Localidad',
            'error': "La Localidad no puede ser borrada pues es Clave de Otros Registros, Contacte al Administrador.",
        })
    else:
        localidad.delete()
    return redirect('georef:lista_localidades')

#Barrios
@permission_required('operadores.menu_georef')
def lista_barrios(request):
    barrios = Barrio.objects.all()
    barrios = barrios.select_related(
        'localidad', 'localidad__departamento', 
        'localidad__departamento__provincia',
        'localidad__departamento__provincia__nacion')
    return render(request, 'lista_barrios.html', {
        'barrios': barrios,
        'has_table': True,
    })

@permission_required('operadores.menu_georef')
def crear_barrio(request, barrio_id=None):
    barrio = None
    if barrio_id:
        barrio = Barrio.objects.get(pk=barrio_id)
    form = BarrioForm(instance=barrio)
    if request.method == "POST":
        form = BarrioForm(request.POST, instance=barrio)
        if form.is_valid():
            form.save()
            return redirect('georef:lista_barrios')
    return render(request, "extras/generic_form.html", {'titulo': "Crear Barrio", 'form': form, 'boton': "Crear", })

@permission_required('operadores.menu_georef')
def delete_barrio(request, barrio_id):
    barrio = Barrio.objects.get(pk=barrio_id)
    if is_related(barrio):
        return render(request, 'extras/error.html', {
            'titulo': 'Eliminar Barrio',
            'error': "El Barrio no puede ser borrada pues es Clave de Otros Registros, Contacte al Administrador.",
        })
    else:
        barrio.delete()
    return redirect('georef:lista_barrios')

#Ubicaciones
@permission_required('operadores.menu_georef')
def lista_ubicaciones(request, tipo=None):
    #Definimos variables necesarias
    ubicaciones = Ubicacion.objects.all()
    #Filtramos
    if tipo:
        ubicaciones = ubicaciones.filter(tipo=tipo)
    #Obtenemos capacidad maxima y disponible:
    cap_maxima = ubicaciones.aggregate(Sum('capacidad_maxima'))['capacidad_maxima__sum']
    cap_ocupada = sum([u.capacidad_ocupada() for u in ubicaciones])
    if cap_maxima:
        cap_disponible = cap_maxima - cap_ocupada
    else:
        cap_disponible = 0
    #Optimizamos
    ubicaciones = ubicaciones.select_related('localidad')
    ubicaciones = ubicaciones.prefetch_related('aislados')
    #Lanzamos listado
    return render(request, 'lista_ubicaciones.html', {
        'ubicaciones': ubicaciones,
        'has_table': True,
        'tipo': tipo,
        'cap_maxima': cap_maxima,
        'cap_ocupada': cap_ocupada,
        'cap_disponible': cap_disponible,
    })

@permission_required('operadores.menu_georef')
def crear_ubicacion(request, ubicacion_id=None):
    ubicacion = None
    if ubicacion_id:
        ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
    form = UbicacionForm(instance=ubicacion)
    if request.method == "POST":
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            return redirect('georef:lista_ubicaciones')
    return render(request, "extras/generic_form.html", {'titulo': "Crear Barrio", 'form': form, 'boton': "Crear", })

@permission_required('operadores.menu_georef')
def ver_ubicacion(request, ubicacion_id=None):
    #Optimizamos
    ubicacion = Ubicacion.objects.select_related('localidad', 'barrio')
    ubicacion = ubicacion.prefetch_related('aislados')
    ubicacion = ubicacion.prefetch_related('turnos_inscripciones', 'turnos_inscripciones__inscripto', 'turnos_inscripciones__inscripto__individuo')
    #Traemos la correspondiente
    ubicacion = ubicacion.get(pk=ubicacion_id)
    return render(request, 'ver_ubicacion.html', {
        'ubicacion': ubicacion,
        'has_table': True,
    })

@permission_required('operadores.menu_georef')
def delete_ubicacion(request, ubicacion_id):
    ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
    if ubicacion.aislados_actuales():
        return render(request, 'extras/error.html', {
            'titulo': 'Eliminar Ubicacion Estrategica',
            'error': "La Ubicacion no puede ser borrada pues es Clave de Otros Registros, Contacte al Administrador.",
        })
    else:
        ubicacion.delete()
    return redirect('georef:lista_ubicaciones')

@permission_required('operadores.menu_georef')
def geopos_ubicacion(request, ubicacion_id):
    ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
    if request.method == "POST":
        #cargamos los datos del form:
        ubicacion.latitud = request.POST['latitud']
        ubicacion.longitud = request.POST['longitud']
        ubicacion.save()
        return redirect('georef:lista_ubicaciones')
    return render(request, "extras/gmap_form.html", {
        'objetivo': ubicacion, 
        'gkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
    })


#Funcion de subida inicial
@staff_member_required
def upload_localidades(request):
    titulo = "Carga Masiva Geografica"
    form = UploadCsvWithPass()
    if request.method == "POST":
        form = UploadCsvWithPass(request.POST, request.FILES)
        if form.is_valid():
            file_data = form.cleaned_data['csvfile'].read().decode("utf-8")
            lines = file_data.split("\n")
            cant = 0
            #Limpiamos la base de datos:
            #Provincia.objects.all().delete()
            #p = Provincia(nombre="Jujuy")
            p.save()
            #GEneramos todos los elementos nuevos
            for linea in lines:
                cant += 1
                linea=linea.split(',')
                if linea[0]:
                    departamento = Departamento.objects.get_or_create(
                        provincia=p,
                        nombre= linea[1])[0]
                    localidad = Localidad.objects.get_or_create(
                        departamento= departamento,
                        nombre= linea[2])[0]
                    localidad.codigo_postal = linea[0]
                    localidad.save()
            return render(request, 'extras/upload_csv.html', {'count': len(lines), })
    #Inicial o por error
    return render(request, "extras/upload_csv.html", {'titulo': titulo, 'form': form, })