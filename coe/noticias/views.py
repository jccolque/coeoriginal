#Imports de python

#Import Standard de Django
from django.shortcuts import render
from django.db.models import Q
from core.forms import SearchForm
#Import Personales
from .models import Noticia

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

#test
def carousel(request):
    noticias = Noticia.objects.filter(destacada=True).order_by('fecha')[:5]
    return render(request, 'carousel.html', {'noticias': noticias,})