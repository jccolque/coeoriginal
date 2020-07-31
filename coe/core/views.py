#Import Python Standard
#Imports de Django
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from documentos.functions import ver_publicadas
#Imports de la app
from .models import Faq
from .tokens import account_activation_token

# Create your views here.
#PUBLICAS:
def home(request):
    versiones = ver_publicadas(limit=5)
    return render(request, 'home.html', {'versiones': versiones, })

def faqs(request):
    faqs_list = Faq.objects.all().order_by('orden')
    return render(request, 'faqs.html', {'faqs': faqs_list, })

def consejos(request):
    return render(request, 'consejos.html', {})

def entregas(request):
    return render(request, 'entregas.html', {})

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
                #Aqui ponemos controles para otros menus
                if user.has_perm("operadores.tablero_comando") and not user.is_superuser:
                    return redirect('informacion:tablero_control')
                else:
                    return redirect('core:menu')
    return render(request, "extras/generic_form.html", {'titulo': "Ingresar al Sistema", 'form': form, 'boton': "Ingresar", 'message': message, })

def home_logout(request):
    logout(request)
    return home(request)

#Menu Principal
@permission_required('operadores.menu_core')
def menu(request):
    return render(request, 'menu_core.html', {})

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
