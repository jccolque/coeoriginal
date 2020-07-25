#Imports Django
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
#Imports extras
#Imports del Proyecto
from core.models import Aclaracion
from operadores.functions import obtener_operador
from consultas.models import Telefonista
#Imports de la app
from .models import DenunciaAnonima
from .forms import EvolucionarForm

# Create your views here.
@permission_required('operadores.denuncias')
def menu(request):
    return render(request, 'menu_denuncias.html', {})

@permission_required('operadores.denuncias')
def lista_denuncias(request, tipo=None, estado=None, telefonista_id=None):
    denuncias = DenunciaAnonima.objects.all()
    #Filtramos si es necesario
    if tipo:
        denuncias = denuncias.filter(tipo=tipo)
    if estado:
        denuncias = denuncias.filter(estado=estado)
    if telefonista_id:
        denuncias = denuncias.filter(telefonista__id=telefonista_id)
    #Si no hay filtros:
    if not tipo and not estado:
        denuncias = denuncias.exclude(estado__in=('RE','BA'))
    #Mostramos la lista
    return render(request, 'lista_denuncias.html', {
        'denuncias': denuncias,
        'has_table': True,
        'refresh': True,
    })

@permission_required('operadores.denuncias')
def ver_denuncia(request, denuncia_id):
    denuncia = DenunciaAnonima.objects.get(pk=denuncia_id)
    return render(request, 'ver_denuncia.html', {
        'denuncia': denuncia,
    })

#Administrador
@permission_required('operadores.denuncias')
def evolucionar_denuncia(request, denuncia_id):
    form = EvolucionarForm()
    if request.method == 'POST':
        form = EvolucionarForm(request.POST)
        if form.is_valid():
            denuncia = DenunciaAnonima.objects.get(pk=denuncia_id)
            #Creamos la aclaracion
            aclaracion = form.save(commit=False)
            aclaracion.modelo = 'DenunciaAnonima'
            aclaracion.operador = obtener_operador(request)
            aclaracion.save()
            #agregamos la aclaracion a la denuncia:
            denuncia.aclaraciones.add(aclaracion)
            denuncia.estado = form.cleaned_data['estado']
            denuncia.save()
            return redirect('denuncias:ver_denuncia', denuncia_id=denuncia.id)
    #Lanzamos form
    return render(request, "extras/generic_form.html", {'titulo': "Evolucionar Denuncia", 'form': form, 'boton': "Confirmar", })

@permission_required('operadores.denuncias')
def eliminar_denuncia(request, denuncia_id):
    denuncia = DenunciaAnonima.objects.get(pk=denuncia_id)
    if request.method == "POST":
        #Creamos aclaracion
        aclaracion = Aclaracion()
        aclaracion.operador = obtener_operador(request)
        aclaracion.descripcion = "Se elimino la Denuncia"
        aclaracion.save()
        #modificamos denuncia
        denuncia.aclaraciones.add(aclaracion)
        denuncia.estado = 'BA'
        denuncia.save()
        return redirect('denuncias:lista_denuncias')
    return render(request, "extras/confirmar.html", {
            'titulo': "Eliminar Denuncia",
            'message': "Si realiza esta accion quedara registrada por su usuario.",
            'has_form': True,
        }
    )