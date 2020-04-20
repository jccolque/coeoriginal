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
from informacion.models import Individuo
#imports de la app
from .models import Permiso, IngresoProvincia
from .forms import PermisoForm, BuscarPermiso, DatosForm, FotoForm
from .forms import IngresoProvinciaForm, IngresanteForm, AprobarForm
from .forms import DUTForm, PlanVueloForm
from .functions import actualizar_individuo
from .functions import buscar_permiso, pedir_permiso, definir_fechas

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
                return redirect('permisos:pedir_permiso', individuo_id=individuo.id, num_doc=individuo.num_doc)
            else:
                form.add_error(None, "No se ha encontrado a Nadie con esos Datos.")
    return render(request, "buscar_permiso.html", {'form': form, })

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
                            if SEND_MAIL:
                                to_email = individuo.email
                                #Preparamos el correo electronico
                                mail_subject = 'Bienvenido al Sistema Centralizado COE!'
                                message = render_to_string('emails/permiso_generado.html', {
                                        'individuo': individuo,
                                        'permiso': permiso,
                                    })
                                #Instanciamos el objeto mail con destinatario
                                email = EmailMessage(mail_subject, message, to=[to_email])
                                email.send()
                return render(request, "ver_permiso.html", {'permiso': permiso, })  
        return render(request, "pedir_permiso.html", {'form': form, 'individuo': individuo, })
    except Individuo.DoesNotExist:
        return redirect('permisos:buscar_permiso')

def completar_datos(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = DatosForm(instance=individuo)
    if request.method == "POST":
        form = DatosForm(request.POST, instance=individuo)
        if form.is_valid():
            form.save()
            return redirect('permisos:pedir_permiso', individuo_id=individuo.id, num_doc=individuo.num_doc)
    return render(request, "extras/generic_form.html", {'titulo': "Corregir/Completar Datos", 'form': form, 'boton': "Guardar", })

def subir_foto(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = FotoForm()
    if request.method == "POST":
        form = FotoForm(request.POST, request.FILES)
        if form.is_valid():
            individuo.fotografia = form.cleaned_data['fotografia']
            individuo.save()
            return redirect('permisos:pedir_permiso', individuo_id=individuo.id, num_doc=individuo.num_doc)
    return render(request, "extras/generic_form.html", {'titulo': "Subir Fotografia", 'form': form, 'boton': "Cargar", })

#Ingreso Provincial
def pedir_ingreso_provincial(request):
    form = IngresoProvinciaForm()
    if request.method == "POST":
        form = IngresoProvinciaForm(request.POST, request.FILES)
        if form.is_valid():
            ingreso = form.save()
            #Enviar email
            if SEND_MAIL:
                to_email = ingreso.email_contacto
                #Preparamos el correo electronico
                mail_subject = 'Requerimiento de Ingreso Provincial Jujuy!'
                message = render_to_string('emails/ingreso_provincial.html', {
                        'ingreso': ingreso,
                    })
                #Instanciamos el objeto mail con destinatario
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
            #Enviarlo a cargar ingresantes
            return redirect('permisos:ver_ingreso_provincial', token=ingreso.token)
    return render(request, "extras/generic_form.html", {'titulo': "Permiso de Ingreso a Jujuy", 'form': form, 'boton': "Cargar", })

#Ingreso Provincial
def ver_ingreso_provincial(request, token):
    ingreso = IngresoProvincia.objects.prefetch_related('individuos')
    ingreso = ingreso.get(token=token)
    return render(request, 'ver_ingreso_provincial.html', {
        'ingreso': ingreso,
        'has_table': True,
    })

#Ingreso Provincial
def cargar_ingresante(request, ingreso_id, individuo_id):
    individuo = None
    if individuo_id:
        individuo = Individuo.objects.get(pk=individuo_id)
    form = IngresanteForm(instance=individuo)
    if request.method == "POST":
        #obtenemos ingreso
        ingreso = IngresoProvincia.objects.get(pk=ingreso_id)
        try:#Tratamos de obtener el dni
            num_doc = request.POST['num_doc']
            individuo = Individuo.objects.get(num_doc=num_doc)
        except Individuo.DoesNotExist:
            individuo = None
        form = IngresanteForm(request.POST, instance=individuo)
        if form.is_valid():
            #actualizamos individuo con los datos nuevos
            individuo = actualizar_individuo(form)
            #Lo agregamos al registro
            ingreso.individuos.add(individuo)
            return redirect('permisos:ver_ingreso_provincial', token=ingreso.token)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Ingresante", 'form': form, 'boton': "Cargar", })

def cargar_dut(request, ingreso_id):
    form = DUTForm()
    if request.method == "POST":
        #obtenemos ingreso
        ingreso = IngresoProvincia.objects.get(pk=ingreso_id)
        form = DUTForm(request.POST, request.FILES, instance=ingreso)
        if form.is_valid():
            form.save()
            return redirect('permisos:ver_ingreso_provincial', token=ingreso.token)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Documento Universal de Transporte", 'form': form, 'boton': "Cargar", })

def cargar_plan_vuelo(request, ingreso_id):
    form = PlanVueloForm()
    if request.method == "POST":
        #obtenemos ingreso
        ingreso = IngresoProvincia.objects.get(pk=ingreso_id)
        form = PlanVueloForm(request.POST, request.FILES, instance=ingreso)
        if form.is_valid():
            form.save()
            return redirect('permisos:ver_ingreso_provincial', token=ingreso.token)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Documento Universal de Transporte", 'form': form, 'boton': "Cargar", })

def quitar_ingresante(request, ingreso_id, individuo_id):
    ingreso = IngresoProvincia.objects.get(pk=ingreso_id)
    individuo = Individuo.objects.get(pk=individuo_id)
    ingreso.individuos.remove(individuo)
    return redirect('permisos:ver_ingreso_provincial', token=ingreso.token)

def ver_ingreso_aprobado(request, ingreso_id):
    pass

#Administrar
@permission_required('operadores.permisos')
def menu_permisos(request):
    return render(request, 'menu_permisos.html', {})

@permission_required('operadores.permisos')
def lista_activos(request):
    permisos = Permiso.objects.filter(endda__gt=timezone.now())
    return render(request, 'lista_permisos.html', {
        'titulo': "Permisos Activos",
        'permisos': permisos,
        'has_table': True,
    })

@permission_required('operadores.permisos')
def lista_vencidos(request):
    permisos = Permiso.objects.filter(endda__lt=timezone.now())
    return render(request, 'lista_permisos.html', {
        'titulo': "Permisos Vencidos",
        'permisos': permisos,
        'has_table': True,
    })

@permission_required('operadores.permisos')
def ver_permiso(request, permiso_id, individuo_id):
    permiso = Permiso.objects.select_related('individuo')
    permiso = permiso.get(pk=permiso_id)
    if individuo_id == permiso.individuo.id:
        return render(request, 'ver_permiso.html', {
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
    permiso = Permiso.objects.get(pk=permiso_id)
    permiso.begda = timezone.now() - timedelta(days=7)#Lo mandamos una semana para atras
    permiso.endda = timezone.now() - timedelta(days=7)#Lo mandamos una semana para atras
    permiso.aclaracion = permiso.aclaracion + ' | Dado de baja por: ' + str(obtener_operador(request))
    permiso.save()
    return redirect('permisos:lista_activos')

#Ingresos Provinciales
@permission_required('operadores.permisos')
def lista_ingresos(request):
    ingresos = IngresoProvincia.objects.exclude(estado='B')
    ingresos = ingresos.prefetch_related('individuos')
    return render(request, 'lista_ingresos.html', {
        'titulo': "Ingresos Pedidos",
        'ingresos': ingresos,
        'has_table': True,
    })

@permission_required('operadores.permisos')
def aprobar_ingreso(request, ingreso_id):
    form = AprobarForm()
    if request.method == 'POST':
        ingreso = IngresoProvincia.objects.get(pk=ingreso_id)
        form = AprobarForm(request.POST)
        if form.is_valid():
            if SEND_MAIL:
                to_email = ingreso.email_contacto
                #Preparamos el correo electronico
                mail_subject = 'Aprobamos tu Ingreso a la Provincia Jujuy!'
                message = render_to_string('emails/ingreso_aprobado.html', {
                        'ingreso': ingreso,
                    })
                #Instanciamos el objeto mail con destinatario
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
            #Aprobamos el Ingreso
            ingreso.estado = 'A'
            ingreso.fecha_llegada = form.cleaned_data['fecha']
            ingreso.save()
            return redirect('permisos:ver_ingreso_provincial', token=ingreso.token)
    return render(request, "extras/generic_form.html", {'titulo': "Aprobar Ingreso Provincial", 'form': form, 'boton': "Aprobar", })

@permission_required('operadores.permisos')
def eliminar_ingreso(request, ingreso_id):
    ingreso = IngresoProvincia.objects.get(pk=ingreso_id)
    ingreso.estado = 'B'
    ingreso.save()
    return redirect('permisos:lista_ingresos')