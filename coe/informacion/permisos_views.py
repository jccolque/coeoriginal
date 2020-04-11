#Imports de Python
from datetime import timedelta
#Imports Django
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
#Imports extras
#Imports del proyecto
from operadores.functions import obtener_operador
#imports de la app
from .models import Individuo, Permiso
from .forms import PermisoForm, BuscarPermiso, DatosForm, FotoForm

#Publico
def buscar_permiso(request):
    form = BuscarPermiso()
    if request.method == 'POST':
        form = BuscarPermiso(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.filter(
                num_doc=form.cleaned_data['num_doc'],
                apellidos__icontains=form.cleaned_data['apellido'])
            if individuo:
                individuo = individuo.first()
                return redirect('permisos_urls:pedir_permiso', individuo_id=individuo.id, num_doc=individuo.num_doc)
            else:
                form.add_error(None, "No se ha encontrado a Nadie con esos Datos.")
    return render(request, "permisos/buscar_permiso.html", {'form': form, })

def pedir_permiso(request, individuo_id, num_doc):
    try:
        individuo = Individuo.objects.get(pk=individuo_id, num_doc=num_doc)
        form = PermisoForm(initial={'individuo': individuo, })
        if request.method == 'POST':
            form = PermisoForm(request.POST, initial={'individuo': individuo, })
            if form.is_valid():
                permiso = form.save(commit=False)
                permiso.individuo = individuo
                permiso.save()
                #Enviar email
                return render(request, "permisos/permiso_entregado.html", {'permiso': permiso, })
        return render(request, "permisos/pedir_permiso.html", {'form': form, 'individuo': individuo, })
    except Individuo.DoesNotExist:
        return redirect('permisos_urls:buscar_permiso')

def completar_datos(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = DatosForm(instance=individuo)
    if request.method == "POST":
        form = DatosForm(request.POST, instance=individuo)
        if form.is_valid():
            form.save()
            return redirect('permisos_urls:pedir_permiso', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Corregir/Completar Datos", 'form': form, 'boton': "Guardar", })

def subir_foto(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = FotoForm()
    if request.method == "POST":
        form = FotoForm(request.POST, request.FILES)
        if form.is_valid():
            individuo.fotografia = form.cleaned_data['fotografia']
            individuo.save()
            return redirect('permisos_urls:pedir_permiso', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Subir Fotografia", 'form': form, 'boton': "Cargar", })

#Administrar
@permission_required('operadores.menu_informacion')
def menu_permisos(request):
    return render(request, 'permisos/menu_permisos.html', {})

@permission_required('operadores.menu_informacion')
def lista_activos(request):
    permisos = Permiso.objects.filter(endda__gt=timezone.now())
    return render(request, 'permisos/lista_permisos.html', {
        'titulo': "Permisos Activos",
        'permisos': permisos,
        'has_table': True,
    })

@permission_required('operadores.menu_informacion')
def lista_vencidos(request):
    permisos = Permiso.objects.filter(endda__lt=timezone.now())
    return render(request, 'permisos/lista_permisos.html', {
        'titulo': "Permisos Vencidos",
        'permisos': permisos,
        'has_table': True,
    })

@permission_required('operadores.menu_informacion')
def ver_permiso(request, permiso_id):
    permiso = Permiso.objects.select_related('individuo')
    permiso = permiso.get(pk=permiso_id)
    return render(request, 'permisos/ver_permiso.html', {
        'individuo': permiso.individuo,
        'permiso': permiso,
    })    

@permission_required('operadores.menu_informacion')
def eliminar_permiso(request, permiso_id):
    print("Damos de baja permiso")
    permiso = Permiso.objects.get(pk=permiso_id)
    permiso.begda = timezone.now() - timedelta(days=7)#Lo mandamos una semana para atras
    permiso.endda = timezone.now() - timedelta(days=7)#Lo mandamos una semana para atras
    permiso.aclaracion = permiso.aclaracion + ' | Dado de baja por: ' + str(obtener_operador(request))
    permiso.save()
    return redirect('permisos_urls:lista_activos')
    