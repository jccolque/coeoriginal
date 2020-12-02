#Imports de python

#Import Standard de Django
from django.shortcuts import render
from django.db.models import Q
from core.forms import SearchForm
#Import Personales
from .models import Noticia
from .models import Parte

# Create your views here.
def ver_noticias(request):
    etiquetas = Noticia.etiquetas.most_common()[:5]
    noticias = Noticia.objects.all().order_by('-fecha')[:10]
    return render(request, 'noticias.html', { 'noticias': noticias, 'form': SearchForm(), 'boton': 'Buscar', 'etiquetas': etiquetas, }) 

def buscar_noticias(request):
    noticias = Noticia.objects.all()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            noticias = noticias.filter(titulo__icontains=search)
            return render(request, 'noticias.html', { 'noticias': noticias, 'form': form, })
    #Si no siempre devolvemos la normal
    return ver_noticias(request)

def buscar_etiqueta(request, tag_id):
    etiquetas = Noticia.etiquetas.most_common()[:5]
    noticias = Noticia.objects.filter(etiquetas__id=tag_id)[:10]
    return render(request, 'noticias.html', { 'noticias': noticias, 'form': SearchForm(), 'boton': 'Buscar', 'etiquetas': etiquetas, })

def ver_noticia(request, noticia_id):
    noticia = Noticia.objects.get(pk=noticia_id)
    return render(request, 'noticia.html', { 'noticia': noticia, 'form': SearchForm(), })


def ver_partes(request):
    etiquetas = Parte.etiquetas.most_common()[:5]
    partes = Parte.objects.all().order_by('-fecha')[:10]
    return render(request, 'partes.html', {
        'partes': partes, 
        'form': SearchForm(), 
        'boton': 'Buscar', 
        'etiquetas': etiquetas, 
    })


def buscar_partes(request):
    partes = Parte.objects.all()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            partes = partes.filter(title__icontains=search)
            return render(request, 'partes.html', {
                'partes': partes, 
                'form': form, 
            })
    #Si no siempre devolvemos la normal
    return ver_partes(request)


def search_etiqueta(request, tag_id):
    etiquetas = Parte.etiquetas.most_common()[:5]
    partes = Parte.objects.filter(etiquetas__id=tag_id)[:10]
    return render(request, 'partes.html', {
        'partes': partes, 
        'form': SearchForm(), 
        'boton': 'Buscar', 
        'etiquetas': etiquetas, 
    })


def ver_parte(request, parte_id):
    parte = Parte.objects.get(pk=parte_id)
    return render(request, 'parte.html', {
        'parte': parte, 
        'form': SearchForm(), 
    })

#test
def carousel(request):
    noticias = Noticia.objects.filter(destacada=True).order_by('fecha')[:5]
    return render(request, 'carousel.html', {'noticias': noticias,})

