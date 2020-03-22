#Import Python Standard
import json
#Imports de Django
from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.template.loader import render_to_string
from django.contrib.auth.forms import AuthenticationForm
#Imports del proyecto
from coe.settings import SEND_MAIL
#Imports de la app
from .models import Faq, Consulta
from .tokens import account_activation_token
from .decoradores import superuser_required, generic_permission_required
from .forms import ConsultaForm

# Create your views here.

#PUBLICAS:
def home(request):
    return render(request, 'home.html', {})

def faqs(request):
    faqs_list = Faq.objects.all().order_by('orden')
    return render(request, 'faqs.html', {'faqs': faqs_list, })

def contacto(request):
    if request.method == 'POST': #En caso de que se haya realizado una busqueda
        consulta_form = ConsultaForm(request.POST)
        if consulta_form.is_valid():
            consulta = consulta_form.save()
            #enviar email de validacion
            to_email = consulta_form.cleaned_data.get('email')#Obtenemos el correo
            #Preparamos el correo electronico
            mail_subject = 'Confirma tu correo de respuesta por la Consultas Realizada al COE2020.'
            message = render_to_string('emails/acc_active_consulta.html', {
                    'consulta': consulta,
                    'token':account_activation_token.make_token(consulta),
                })
            #Instanciamos el objeto mail con destinatario
            email = EmailMessage(mail_subject, message, to=[to_email])
            #Enviamos el correo
            if SEND_MAIL:
                email.send()
            return render(request, 'contacto.html', {})
    else:
        consulta_form = ConsultaForm()
    return render(request, 'contacto.html', {"form": consulta_form,
                'titulo': "Envianos una consulta:", 'boton': "Enviar"})

#Manejo de sesiones de Usuarios
def home_login(request):
    message = ''
    form = AuthenticationForm()
    if request.method == "POST":
        # Añadimos los datos recibidos al formulario
        form = AuthenticationForm(data=request.POST)
        # Si el formulario es válido...
        if form.is_valid():
            # Recuperamos las credenciales validadas
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Verificamos las credenciales del usuario
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return home(request)
    return render(request, "extras/generic_form.html", {'titulo': "Ingresar al Sistema", 'form': form, 'boton': "Ingresar", 'message': message, })

def home_logout(request):
    logout(request)
    return home(request)

#Activar mails
def activar_usuario_mail(request, usuario_id, token):
    try:
        usuario = User.objects.get(pk=usuario_id)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        usuario = None
    if usuario and account_activation_token.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        texto = 'Excelente! Su correo electronico fue validada.'
    else:
        texto = 'El link de activacion es invalido!'
    return render(request, 'extras/resultado.html', {'texto': texto, })

#activa consultas
def activar_consulta(request, consulta_id, token):
    try:
        consulta = Consulta.objects.get(pk=consulta_id)
    except(TypeError, ValueError, OverflowError, Consulta.DoesNotExist):
        consulta = None
    if consulta and account_activation_token.check_token(consulta, token):
        consulta.valida = True
        consulta.save()
        texto = 'Excelente! Su correo electronico fue validada.'
    else:
        texto = 'El link de activacion es invalido!'
    return render(request, 'extras/resultado.html', {'texto': texto, })

#Web Servis generico para todas las apps del sistema
#Si el modelo tiene as_dict, aparece.
@superuser_required
def ws(request, nombre_app=None, nombre_modelo=None):
    if nombre_app and nombre_modelo:
        if apps.all_models[nombre_app][nombre_modelo.lower()]:
            modelo = apps.all_models[nombre_app][nombre_modelo.lower()]
            if hasattr(modelo, 'as_dict'):
                datos = modelo.objects.all()
                datos = [d.as_dict() for d in datos]
                return HttpResponse(json.dumps({nombre_modelo+'s': datos, "cant_registros": len(datos),}), content_type='application/json')

    apps_listas = {}
    for app, models in apps.all_models.items():
        for model in models.values():
            if hasattr(model, 'as_dict'):
                if app in apps_listas:
                    apps_listas[app].append(model._meta.model_name)
                else:
                    apps_listas[app] = [model._meta.model_name, ]
    return render(request, 'ws.html', {"apps_listas": apps_listas,})