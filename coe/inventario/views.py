#Imports Django
import csv
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from core.forms import SearchForm
from operadores.functions import obtener_operador
#Imports app
from .models import SubGrupo
from .models import Item, EventoItem
from .models import GeoPosicion
from .forms import ItemForm, ModItemForm
from .forms import EventoItemForm, TransferirForm

# Create your views here.
@permission_required('operadores.menu_inventario')
def menu(request):
    return render(request, 'menu_inventario.html', {})

#ITEMS:
@permission_required('operadores.menu_inventario')
def lista_general(request):
    subgrupos = SubGrupo.objects.all()
    subgrupos = subgrupos.select_related('rubro')
    subgrupos = subgrupos.prefetch_related('items', 'items__eventos')
    return render(request, 'lista_general.html', {'subgrupos': subgrupos, })

@permission_required('operadores.menu_inventario')
def lista_detallada(request, rubro_id=None, subgrupo_id=None):
    items = Item.objects.all()
    items = items.select_related('subgrupo', 'subgrupo__rubro', 'responsable', )
    items = items.prefetch_related('eventos')
    if rubro_id:
        items = items.filter(subgrupo__rubro__id=rubro_id)
    if subgrupo_id:
        items = items.filter(subgrupo__id=subgrupo_id)
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data["search"]
            items = items.filter(
                Q(nombre__icontains=search) |
                Q(subgrupo__nombre__icontains=search) |
                Q(subgrupo__rubro__nombre__icontains=search)
            )
    return render(request, 'lista_detallada.html', {'items': items, })

@permission_required('operadores.menu_inventario')
def ver_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    return render(request, 'ver_item.html', {'item': item, })

@permission_required('operadores.menu_inventario')
def crear_item(request, item_id=None):
    item = None
    if item_id:
        item = Item.objects.get(pk=item_id)
        form = ModItemForm(instance=item)
    else:
        form = ItemForm()
    if request.method == "POST":
        if item_id:
            form = ModItemForm(request.POST, instance=item)
            if form.is_valid():
                item = form.save()
                return redirect('inventario:ver_item', item_id=item.id)
        else:
            form = ItemForm(request.POST)
            if form.is_valid():
                item = form.save()
                evento = EventoItem()
                evento.item = item
                evento.accion = 'I'
                evento.cantidad = form.cleaned_data['cantidad']
                evento.actuante = form.cleaned_data['actuante']
                evento.operador = obtener_operador(request)
                evento.detalle = 'Carga inicial en el Sistema'
                evento.save()
                return redirect('inventario:ver_item', item_id=item.id)
    return render(request, "extras/generic_form.html", {'titulo': "Crear Item", 'form': form, 'boton': "Agregar", })

@permission_required('operadores.menu_inventario')
def cargar_geoposicion(request, item_id=None):
    item = Item.objects.get(pk=item_id)
    if request.method == "POST":
        if hasattr(item,'geoposicion'):
            geoposicion = item.geoposicion
        else:
            geoposicion = GeoPosicion()
            geoposicion.item = item
        #cargamos los datos del form:
        geoposicion.latitud = request.POST['latitud']
        geoposicion.longitud = request.POST['longitud']
        geoposicion.observaciones = request.POST['observaciones']
        geoposicion.save()
        return redirect('inventario:ver_item', item_id=item.id)
    return render(request, "extras/gmap_form.html", {
        'objetivo': item, 
        'gkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
    })

#Administracion de items
@permission_required('operadores.menu_inventario')
def crear_evento(request, item_id=None):
    item = Item.objects.get(pk=item_id)
    form = EventoItemForm(initial={'item':item})
    if request.method == "POST":
        form = EventoItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:ver_item', item_id=item.id)
    return render(request, "extras/generic_form.html", {'titulo': "Crear Evento del Item", 'form': form, 'boton': "Agregar", })

@permission_required('operadores.menu_inventario')
def devolver_item(request, evento_id):
    evento = EventoItem.objects.get(pk=evento_id)
    evento.devuelto = True
    evento.save()
    devuelto = evento
    devuelto.id = None
    devuelto.accion = 'I'
    devuelto.fecha = timezone.now()
    devuelto.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@permission_required('operadores.menu_inventario')
def transferir_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    form = TransferirForm()
    if request.method == "POST":
        form = TransferirForm(request.POST)
        if form.is_valid():
            operador = obtener_operador(request)
            #Retiramos el item
            evento_retiro = EventoItem()
            evento_retiro.item = item
            evento_retiro.accion = 'R'
            evento_retiro.cantidad = form.cleaned_data['cantidad']
            evento_retiro.actuante = form.cleaned_data['actuante']
            evento_retiro.detalle = form.cleaned_data['detalle'] + " A " + str(form.cleaned_data['destino'])
            evento_retiro.operador = operador
            evento_retiro.save()
            #Ingresamos el item
            evento_ingreso = EventoItem()
            evento_ingreso.item = form.cleaned_data['destino']
            evento_ingreso.accion = 'I'
            evento_ingreso.cantidad = form.cleaned_data['cantidad']
            evento_ingreso.actuante = form.cleaned_data['actuante']
            evento_ingreso.detalle = form.cleaned_data['detalle'] + " Deste " + str(item)
            evento_ingreso.operador = operador
            evento_ingreso.save()
            return redirect('inventario:ver_item', item_id=evento_ingreso.item.id)
    return render(request, "extras/generic_form.html", {'titulo': "Transferir "+str(item), 'form': form, 'boton': "Transferir", })

@permission_required('operadores.menu_inventario')
def csv_inventario(request):
    items = Item.objects.all()
    items = items.select_related('subgrupo', 'subgrupo__rubro')
    #Iniciamos la creacion del csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventario.csv"'
    writer = csv.writer(response)
    writer.writerow(['REPORTE DE INVENTARIO'])
    writer.writerow(['RUBRO', 'SUBGRUPO', 'NOMBRE', 'CANTIDAD DISPONIBLE', 'CANTIDAD DISTRIBUIDA'])
    for item in items:
        writer.writerow([
            item.subgrupo.rubro.nombre,
            item.subgrupo.nombre,
            item.nombre,
            item.cantidad_disponible(),
            item.cantidad_distribuida(),
        ])
    #Enviamos el archivo para descargar
    return response