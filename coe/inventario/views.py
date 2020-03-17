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
from .models import Item, EventoItem
from .forms import ItemForm, EventoItemForm

# Create your views here.
@permission_required('operadores.menu_inventario')
def menu(request):
    return render(request, 'menu_inventario.html', {})

#ITEMS:
@permission_required('operadores.ver_item')
def lista_items(request, rubro_id=None, subgrupo_id=None):
    items = Item.objects.all()
    if rubro_id:
        items = items.filter(rubro__id=rubro_id)
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
    return render(request, 'lista_items.html', {'items': items, })

@permission_required('operadores.ver_item')
def ver_item(request, item_id):
    item = Item.objects.get(pk=item_id)
    return render(request, 'ver_item.html', {'item': item, })

@permission_required('operadores.crear_item')
def crear_item(request, item_id=None):
    item = None
    if item_id:
        item = Item.objects.get(pk=item_id)
    form = ItemForm(instance=item)
    if request.method == "POST":
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

@permission_required('operadores.crear_item')
def crear_evento(request, item_id=None):
    item = Item.objects.get(pk=item_id)
    form = EventoItemForm(initial={'item':item})
    if request.method == "POST":
        form = EventoItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario:ver_item', item_id=item.id)
    return render(request, "extras/generic_form.html", {'titulo': "Crear Evento del Item", 'form': form, 'boton': "Agregar", })

@permission_required('operadores.crear_item')
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