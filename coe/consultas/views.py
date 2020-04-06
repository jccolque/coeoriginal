#Imports Django
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
from django.core.mail import EmailMessage
#Imports del proyecto
from coe.settings import SEND_MAIL
from core.tokens import account_activation_token
from operadores.functions import obtener_operador
#Imports de la app
from .models import Consulta
from .forms import ConsultaForm, RespuestaForm


#Consultas
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

#Administracion Consultas
@permission_required('operadores.menu_consultas')
def menu(request):
    return render(request, 'menu_consultas.html', {})

@permission_required('operadores.menu_consultas')
def lista_consultas(request):
    consultas = Consulta.objects.filter(valida=True, respondida=False)
    return render(request, 'lista_consultas.html', {
        "consultas": consultas, 
        "has_table": True,
        "refresh": True,
    })

@permission_required('operadores.menu_consultas')
def lista_respondidas(request):
    consultas = Consulta.objects.filter(respondida=True)
    return render(request, 'lista_respondidas.html', {
        "consultas": consultas,
        "has_table": True,
    })

@permission_required('operadores.menu_consultas')
def ver_consulta(request, consulta_id):
    form = RespuestaForm()
    consulta = Consulta.objects.get(pk=consulta_id)
    if request.method == "POST":
        form = RespuestaForm(request.POST)
        if form.is_valid():
            #Preparamos el objeto respuesta
            respuesta = form.save(commit=False)
            respuesta.operador = obtener_operador(request)
            respuesta.consulta = consulta
            #enviar email de respuesta
            to_email = consulta.email
            #Preparamos el correo electronico
            mail_subject = 'COE2020: Respondimos tu Consulta ' + consulta.asunto
            message = render_to_string('emails/respuesta_consulta.html', {
                    'consulta': consulta,
                    'respuesta':respuesta,
                })
            #Instanciamos el objeto mail con destinatario
            email = EmailMessage(mail_subject, message, to=[to_email])
            #Enviamos el correo
            if SEND_MAIL:
                email.send()
                #La marcamos como respondida
                consulta.respondida = True
                consulta.save()
                #Guardamos la respuesta
                consulta.save()
            return redirect('consultas:lista_consultas')
    return render(request, 'ver_consulta.html', {"consulta": consulta, 'form': form, })

@permission_required('operadores.menu_consultas')
def consulta_respondida(request, consulta_id):
    consulta = Consulta.objects.get(pk=consulta_id)
    consulta.respondida = True
    consulta.save()
    return redirect('consultas:lista_consultas')

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