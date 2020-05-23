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
#imports de la app
from .models import Organization, Domic_o
from .forms import OrganizationForm, EmpleadoForm, EmpleadoFormset
from .forms import OrgaForm



#Publico
def pedir_coca(request):

    return render(request, "pedir_coca.html", {'title': "Sistema de Provisión de Coca", })


def buscar_organizacion(request):

    return render(request, "buscar_organizacion.html", {'form': form,})

def disclaimer_org(request, ):
    form = OrganizationForm()    
    if request.method == 'POST':
        #Obtenemos peticion
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            organizacion = form.save()
            if form.cleaned_data['dom_localidad']:
                domicilio = Domic_o()
                domicilio.organizacion = organizacion
                domicilio.localidad = form.cleaned_data['dom_localidad']
                domicilio.calle = form.cleaned_data['dom_calle']
                domicilio.barrio = form.cleaned_data['dom_barrio']
                domicilio.manzana = form.cleaned_data['dom_manzana']
                domicilio.lote = form.cleaned_data['dom_lote']
                domicilio.piso = form.cleaned_data['dom_piso']
                domicilio.save()
        else: 
            return render(request, "organizacion_peticion.html", {'title': 'Petición de Coca - ORGANIZACIONES', 'form': form, 'message': 'Formulario no valido.', 'button': 'SOLICITAR COCA' })

    return render(request, "organizacion_peticion.html", {'title': 'Petición de Coca - ORGANIZACIONES', 'form': form, 'button': 'SOLICITAR COCA'})