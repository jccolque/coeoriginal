#Imports de Python
import math
from datetime import timedelta
#Imports Django
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
#Imports extras
#Imports del proyecto
from coe.settings import SEND_MAIL
from core.decoradores import superuser_required
from core.forms import EmailForm, UploadFoto
from core.functions import date2str
from operadores.functions import obtener_operador
from informacion.models import Individuo, Atributo
from informacion.functions import actualizar_individuo
from informacion.forms import BuscarIndividuoSeguro
from graficos.functions import obtener_grafico
#imports de la app
from informacion.models import Individuo, Domicilio
from .models import Organization, Domic_o, Peticionp, Emails_Peticionp
from .forms import OrganizationForm, EmpleadoForm, EmpleadoFormset
from .forms import PeticionpForm
from .forms import PersonapetForm, AprobarForm

#Publico
def pedir_coca(request):

    return render(request, "pedir_coca.html", {'title': "Sistema de Provisión de Coca", })

def peticion_persona(request, peticionp_id=None):
    peticion = None
    if peticionp_id:
        peticion = Peticionp.objects.get(pk=peticionp_id)
    form = PeticionpForm(instance=peticion)
    if request.method == "POST":
        form = PeticionpForm(request.POST, request.FILES, instance=peticion)
        if form.is_valid():
            peticion = form.save()
            #Enviar email
            if SEND_MAIL:
                to_email = peticion.email_contacto
                #Preparamos el correo electronico
                mail_subject = 'COE2020 Requerimiento de Ingreso Provincial Jujuy!'
                message = render_to_string('emails/email_persona_pet.html', {
                    'peticion': peticion,
                })
                #Instanciamos el objeto mail con destinatario
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
            #Enviarlo a cargar ingresantes
            return redirect('provision:ver_peticion_persona', token=peticion.token)
        else: 
            return render(request, "peticion_persona.html", {'title': "PETICIÓN DE COCA - PERSONAS", 'form': form, 'button': "Iniciar Pedido", 'message': 'FORMULARIO INVÁLIDO, CORRIJA DATOS.' })

    return render(request, "peticion_persona.html", {'title': "PETICIÓN DE COCA - PERSONAS", 'form': form, 'button': "Iniciar Pedido", })

def ver_peticion_persona(request, token):
    peticion = Peticionp.objects.prefetch_related('individuos')
    peticion = peticion.get(token=token)
    #Calcular Limite para eliminacion
    limite = int(72 - (timezone.now() - peticion.fecha).total_seconds() / 3600)
    return render(request, 'panel_peticion.html', {
        'peticion': peticion,
        'limite': limite,        
        'has_table': True,
    })

def cargar_people(request, peticion_id, individuo_id=None):
    individuo = None
    if individuo_id:
        individuo = Individuo.objects.get(pk=individuo_id)
    form = PersonapetForm(instance=individuo)
    if request.method == "POST":
        #obtenemos peticion
        peticion = PersonapetFormobjects.get(pk=ingreso_id)
        try:#Tratamos de obtener el dni
            num_doc = request.POST['num_doc']
            individuo = Individuo.objects.get(num_doc=num_doc)
        except Individuo.DoesNotExist:
            individuo = None
        form = PersonapetForm(request.POST, request.FILES, instance=individuo)
        if form.is_valid():
            #actualizamos individuo con los datos nuevos
            individuo = actualizar_individuo(form)            
            individuo.destino = peticion.destino
            individuo.save()
            #Lo agregamos al registro
            peticion.individuos.add(individuo)
            return redirect('provision:ver_peticion_persona', token=peticion.token)
    return render(request, "cargar_people.html", {'title': "Cargar Datos Personales", 'form': form, 'button': "Cargar", }) 

def quitar_persona(request, peticion_id, individuo_id):
    peticion = Pedidosp.objects.get(pk=peticion_id)
    individuo = Individuo.objects.get(pk=individuo_id)
    peticion.individuos.remove(individuo)
    return redirect('provision:ver_peticion_persona', token=peticion.token)

def finalizar_peticion(request, peticion_id):
    peticion = Peticionp.objects.get(pk=peticion_id)    
    #Chequear que el ingreso este finalizado
    if not peticion.individuos.exists():
        return render(request, 'extras/error.html', {
            'titulo': 'FINALIZACIÓN DEGENEGADA',
            'error': "USTED DEBE CARGAR SUS DATOS PERSONALES",
        })    
    #Pasar a estado finalizado    
    peticion.estado = 'E'
    peticion.save()
    return redirect('provision:ver_peticion_persona', token=peticion.token)

#Administrar
@permission_required('operadores.menu_provisiones')
def menu_provision(request):
    return render(request, 'menu_provisiones.html', {})

@permission_required('operadores.menu_provisiones')
def lista_peticiones(request, estado=None):
    peticion = Peticionp.objects.all()
    #Filtramos de ser necesario
    if not estado:
        peticion = peticion.exclude(estado='B')
    if estado:
        peticion = peticion.filter(estado=estado)
    #Optimizamos
    peticion = peticion.select_related('destino', 'operador')
    peticion = peticion.prefetch_related('individuos')
    #Lanzamos listado
    return render(request, 'lista_peticiones.html', {
        'title': "Ingresos Pedidos",
        'peticion': peticion,
        'has_table': True,
    })

@permission_required('operadores.menu_provisiones')
def lista_peticiones_completas(request):
    peticion = Peticionp.objects.filter(estado='E')    
    #Optimizamos
    peticion = peticion.select_related('destino', 'operador')
    peticion = peticion.prefetch_related('individuos', 'individuos__domicilio_actual', 'individuos__domicilio_actual__localidad')
    peticion = peticion.prefetch_related('individuos__documentos')
    #Lanzamos listado
    return render(request, 'lista_peticiones.html', {
        'title': "Peticiones Completass Esperando Aprobacion",
        'peticion': peticion,
        'has_table': True,
    })

@permission_required('operadores.menu_provisiones')
def peticion_enviar_email(request, peticion_id):
    peticion = Peticionp.objects.get(pk=peticion_id)
    form = EmailForm(initial={'destinatario': peticion.email_contacto})
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            if SEND_MAIL:
                to_email = form.cleaned_data['destinatario']
                #Preparamos el correo electronico
                mail_subject = form.cleaned_data['asunto']
                message = render_to_string('emails/ingreso_contacto.html', {
                        'peticion': peticion,
                        'cuerpo': form.cleaned_data['cuerpo'],
                    })
                #Guardamos el mail
                Emails_Peticionp(peticion=peticion, asunto=mail_subject, cuerpo=form.cleaned_data['cuerpo'], operador=obtener_operador(request)).save()
                #Instanciamos el objeto mail con destinatario
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
        return redirect('provision:ver_peticion_persona', token=peticion.token)
    return render(request, "extras/generic_form.html", {'titulo': "Enviar Correo Electronico", 'form': form, 'boton': "Enviar", })

@permission_required('operadores.menu_provisiones')
def peticion_enviado(request, peticion_id):
    peticion = Peticionp.objects.get(pk=peticion_id)
    peticion.estado = 'N'
    peticion.save()
    return redirect('provision:ver_peticion_persona', token=peticion.token)

         
@permission_required('operadores.menu_provisiones')
def eliminar_peticion(request, peticion_id):
    peticion = Peticionp.objects.get(pk=peticion_id)
    peticion.estado = 'B'
    peticion.operador = obtener_operador(request)
    peticion.save()
    return redirect('provision:lista_peticiones')