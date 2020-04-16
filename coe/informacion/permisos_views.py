#Imports de Python
from datetime import timedelta
#Imports Django
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
#Imports extras
#Imports del proyecto
from coe.settings import SEND_MAIL
from operadores.functions import obtener_operador
#imports de la app
from .models import Individuo, Permiso
from .geofence import buscar_permiso, pedir_permiso, definir_fechas
from .permisos_form import PermisoForm, BuscarPermiso, DatosForm, FotoForm

#Publico
def buscar_permiso_web(request):
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

def pedir_permiso_web(request, individuo_id, num_doc):
    try:
        individuo = Individuo.objects.get(pk=individuo_id, num_doc=num_doc)
        form = PermisoForm(initial={'individuo': individuo, })
        if request.method == 'POST':
            form = PermisoForm(request.POST, initial={'individuo': individuo, })
            if form.is_valid():
                permiso = buscar_permiso(individuo)
                if not permiso:
                    permiso = form.save(commit=False)
                    permiso.individuo = individuo
                    permiso.localidad = individuo.domicilio_actual.localidad
                    permiso = pedir_permiso(individuo, permiso.tipo, permiso=permiso)
                    if permiso.aprobar:
                        permiso = definir_fechas(permiso, permiso.begda)
                        if not permiso.pk:
                            permiso.save()
                            #Enviar email
                            to_email = individuo.email
                            #Preparamos el correo electronico
                            mail_subject = 'Bienvenido al Sistema Centralizado COE!'
                            message = render_to_string('emails/permiso_generado.html', {
                                    'individuo': individuo,
                                    'permiso': permiso,
                                })
                            #Instanciamos el objeto mail con destinatario
                            email = EmailMessage(mail_subject, message, to=[to_email])
                            #Enviamos el correo
                            if SEND_MAIL:
                                email.send()
                return render(request, "permisos/ver_permiso.html", {'permiso': permiso, })  
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
            return redirect('permisos_urls:pedir_permiso', individuo_id=individuo.id, num_doc=individuo.num_doc)
    return render(request, "extras/generic_form.html", {'titulo': "Corregir/Completar Datos", 'form': form, 'boton': "Guardar", })

def subir_foto(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = FotoForm()
    if request.method == "POST":
        form = FotoForm(request.POST, request.FILES)
        if form.is_valid():
            individuo.fotografia = form.cleaned_data['fotografia']
            individuo.save()
            return redirect('permisos_urls:pedir_permiso', individuo_id=individuo.id, num_doc=individuo.num_doc)
    return render(request, "extras/generic_form.html", {'titulo': "Subir Fotografia", 'form': form, 'boton': "Cargar", })

#Administrar
@permission_required('operadores.permisos')
def menu_permisos(request):
    return render(request, 'permisos/menu_permisos.html', {})

@permission_required('operadores.permisos')
def lista_activos(request):
    permisos = Permiso.objects.filter(endda__gt=timezone.now())
    return render(request, 'permisos/lista_permisos.html', {
        'titulo': "Permisos Activos",
        'permisos': permisos,
        'has_table': True,
    })

@permission_required('operadores.permisos')
def lista_vencidos(request):
    permisos = Permiso.objects.filter(endda__lt=timezone.now())
    return render(request, 'permisos/lista_permisos.html', {
        'titulo': "Permisos Vencidos",
        'permisos': permisos,
        'has_table': True,
    })

@permission_required('operadores.permisos')
def ver_permiso(request, permiso_id, individuo_id):
    permiso = Permiso.objects.select_related('individuo')
    permiso = permiso.get(pk=permiso_id)
    if individuo_id == permiso.individuo.id:
        return render(request, 'permisos/ver_permiso.html', {
            'individuo': permiso.individuo,
            'permiso': permiso,
        })
    else:
        return render(request, 'extras/error.html', {
            'titulo': 'Permiso Inexistente',
            'error': "El permiso al que intenta acceder no existe.",
        })

@permission_required('operadores.permisos')
def eliminar_permiso(request, permiso_id):
    print("Damos de baja permiso")
    permiso = Permiso.objects.get(pk=permiso_id)
    permiso.begda = timezone.now() - timedelta(days=7)#Lo mandamos una semana para atras
    permiso.endda = timezone.now() - timedelta(days=7)#Lo mandamos una semana para atras
    permiso.aclaracion = permiso.aclaracion + ' | Dado de baja por: ' + str(obtener_operador(request))
    permiso.save()
    return redirect('permisos_urls:lista_activos')
    