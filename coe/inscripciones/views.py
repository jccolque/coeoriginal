#Imports de Django
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from core.forms import SearchForm
from core.functions import paginador
#Impors de la app
from .tokens import account_activation_token
from .models import Inscripto
from .forms import InscriptoForm

# Create your views here.
@permission_required('operadores.menu_inscripciones')
def menu(request):
    return render(request, 'menu_inscripciones.html', {})

def cargar_inscripcion(request):
    form = InscriptoForm()
    if request.method == "POST":
        form = InscriptoForm(request.POST, request.FILES)
        if form.is_valid():
            inscripto = form.save()
            #enviar email de validacion
            to_email = inscripto.email
            #Preparamos el correo electronico
            mail_subject = 'Inscripcion al COE2020'
            message = render_to_string('emails/acc_active_inscripcion.html', {
                    'inscripto': inscripto,
                    'token':account_activation_token.make_token(inscripto),
                })
            #Instanciamos el objeto mail con destinatario
            email = EmailMessage(mail_subject, message, to=[to_email])
            #Enviamos el correo
            email.send()
            return render(request, 'inscripto_exito.html', {'inscripto': inscripto, })
    return render(request, "extras/generic_form.html", {'titulo': "Inscribite", 'form': form, 'boton': "Inscribirse", })

@permission_required('operadores.menu_inscripciones')
def lista_inscriptos(request, profesion_id=None):
    inscriptos = Inscripto.objects.filter(disponible=True)
    if profesion_id:
        inscriptos = inscriptos.filter(profesion=profesion_id)
    #Agregar buscador
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            inscriptos = inscriptos.filter(apellidos__icontains=search)
    inscriptos = paginador(request, inscriptos)
    return render(request, 'lista_inscripciones.html', {'inscriptos': inscriptos, })

@permission_required('operadores.menu_inscripciones')
def ver_inscripto(request, inscripto_id=None):
    inscripto = Inscripto.objects.get(pk=inscripto_id)
    return render(request, 'ver_inscripto.html', {'inscripto': inscripto, })

#Activar:
def activar_inscripcion_mail(request, inscripcion_id, token):
    try:
        inscripto = Inscripto.objects.get(pk=inscripcion_id)
    except(TypeError, ValueError, OverflowError, Inscripto.DoesNotExist):
        inscripto = None
    if inscripto and account_activation_token.check_token(inscripto, token):
        inscripto.valido = True
        inscripto.save()
        texto = 'Excelente! Su correo electronico fue validada.'
    else:
        texto = 'El link de activacion es invalido!'
    return render(request, 'extras/resultado.html', {'texto': texto, })