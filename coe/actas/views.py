#Imports Django
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from core.forms import SearchForm
from operadores.models import Operador
#Imports de la app
from .models import Acta, Participe
from .forms import CrearActaForm

# Create your views here.
@permission_required('operadores.menu_actas')
def menu(request):
    return render(request, 'menu_actas.html', {})

@permission_required('operadores.ver_acta')
def listar_actas(request):
    actas = Acta.objects.all()
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            actas = actas.filter(titulo__icontains=form.cleaned_data['search'])
    return render(request, 'lista_actas.html', {'actas': actas, })

@permission_required('operadores.ver_acta')
def ver_acta(request, acta_id):
    acta = Acta.objects.get(id=acta_id)
    return render(request, 'ver_acta.html', {'acta': acta, })

@permission_required('operadores.crear_acta')
def crear_acta(request, acta_id=None):
    acta = None
    participes = []
    if acta_id:
        acta = Acta.objects.get(pk=acta_id)
        participes = [p.operador.id for p in acta.participes.all()]
    form = CrearActaForm(
        instance=acta,
        initial={'participes': participes})
    if request.method == "POST":
        form = CrearActaForm(request.POST, instance=acta)
        if form.is_valid():
            acta = form.save()
            Participe.objects.filter(acta=acta).delete()
            for operador_id in form.cleaned_data['participes']:
                op = Operador.objects.get(pk=operador_id)
                Participe(acta=acta, operador=op).save()
            return redirect('actas:ver_acta', acta_id=acta.id)
    return render(request, "crear_acta.html", {'form': form, })
