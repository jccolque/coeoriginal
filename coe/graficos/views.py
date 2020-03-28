#Imports de Django
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
#Imports del Proyecto

#Imports de la app
from .models import Grafico, Dato
from .forms import GraficoForm, DatoForm

# Create your views here.
@permission_required('operadores.menu_graficos')
def menu(request):
    return render(request, 'menu_graficos.html', {})

@permission_required('operadores.menu_graficos')
def lista_graficos(request, tipo_id=None):
    graficos = Grafico.objects.all()
    #Filtramos si fue requerido
    if tipo_id:
        graficos = graficos.filter(tipo=tipo_id)
    #Entregamos lista
    return render(request, 'lista_graficos.html', {
        'graficos': graficos,
        'has_table': True,
    })

@permission_required('operadores.menu_graficos')
def ver_grafico(request, grafico_id):
    grafico = Grafico.objects.get(pk=grafico_id)
    #Agregar logica para tipo de graficos segun tipo

    return render(request, 'ver_grafico.html', {
        'grafico': grafico,
        'has_table': True,
    })

#administracion de graficos
@permission_required('operadores.menu_graficos')
def crear_grafico(request, grafico_id=None):
    grafico = None
    if grafico_id:
        grafico = Grafico.objects.get(pk=grafico_id)
    form = GraficoForm(instance=grafico)
    if request.method == "POST":
        form = GraficoForm(request.POST, instance=grafico)
        if form.is_valid():
            grafico = form.save()
            return redirect('graficos:ver_grafico', grafico_id=grafico.id)
    return render(request, "extras/generic_form.html", {'titulo': "Crear/Modificar Grafico", 'form': form, 'boton': "Confirmar", })

@permission_required('operadores.menu_graficos')
def reniciar_datos(request, grafico_id):
    grafico = Grafico.objects.get(pk=grafico_id)
    #Eliminamos todos sus datos
    grafico.datos.all().delete()
    #Quitamos su ultima actualizacion
    grafico.update = None
    grafico.save()
    return redirect('graficos:lista_graficos')

@permission_required('operadores.menu_graficos')
def cambiar_estado(request, grafico_id):
    grafico = Grafico.objects.get(pk=grafico_id)
    grafico.publico = not grafico.publico
    grafico.save()
    return redirect('graficos:ver_grafico', grafico_id=grafico.id)

@permission_required('operadores.menu_graficos')
def crear_dato(request, grafico_id, dato_id=None):
    grafico = Grafico.objects.get(pk=grafico_id)
    dato = None
    if dato_id:
        dato = Dato.objects.get(pk=dato_id)
    form = DatoForm(instance=dato)
    if request.method == "POST":
        form = DatoForm(request.POST, instance=dato)
        if form.is_valid():
            dato = form.save(commit=False)
            dato.grafico = grafico
            dato.save()
            return redirect('graficos:ver_grafico', grafico_id=grafico.id)
    return render(request, "extras/generic_form.html", {'titulo': "Crear/Modificar Dato", 'form': form, 'boton': "Confirmar", })