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
from informacion.models import Individuo, Domicilio
from .models import Organization, Domic_o
from .forms import OrganizationForm, EmpleadoForm, EmpleadoFormset
from .forms import OrgaForm, DniForm, PersonaForm



#Publico
def pedir_coca(request):

    return render(request, "pedir_coca.html", {'title': "Sistema de Provisión de Coca", })


def buscar_organizacion(request):
    form = OrgaForm()
    if request.method == 'POST':
        form = OrgaForm(request.POST)
        if form.is_valid():
            cuit = form.cleaned_data['cuit']                      
            try:
                organizacion = Organization.objects.get(cuit=cuit)
                return redirect('provision:editar_disclaimer_org', organization_id=organizacion.id, cuit=cuit)
            except Organization.DoesNotExist:
                return redirect('provision:cargar_disclaimer_org', cuit=cuit)
        else:
            return render(request, "buscar_organizacion.html", {'title': "INGRESE DATOS", 'form': form, 'button': 'BUSCAR', 'message': 'FORMULARIO NO VÁLIDO',})
        
    return render(request, "buscar_organizacion.html", {'title': "INGRESE DATOS",'form': form, 'button': 'BUSCAR'})

def buscar_persona(request):
    form = DniForm()
    if request.method == 'POST':
        form = DniForm(request.POST)
        if form.is_valid():
            num_doc = form.cleaned_data['num_doc']
            num_doc = num_doc.upper()                      
            try:
                individuo = Individuo.objects.get(num_doc=num_doc)
                return redirect('provision:edit_persona', individuo_id=individuo.id, num_doc=num_doc)
            except Individuo.DoesNotExist:
                return redirect('provision:cargar_persona', num_doc=num_doc)
        else:
            return render(request, "buscar_persona.html", {'title': "INGRESE DATOS", 'form': form, 'button': 'BUSCAR', 'message': 'FORMULARIO NO VÁLIDO',})
        
    return render(request, "buscar_persona.html", {'title': "INGRESE DATOS",'form': form, 'button': 'BUSCAR PERSONA'})

def cargar_persona(request, num_doc=None):
    form = PersonaForm(initial={"num_doc": num_doc})
    #Analizamos si mando informacion
    if request.method == "POST":
        form = PersonaForm(request.POST)
        if form.is_valid():
            persona = form.save(commit=False)
            persona.save()
            #Creamos domicilio
            domicilio = Domicilio()
            domicilio.individuo = persona
            if form.cleaned_data['localidad']:
                domicilio.localidad = form.cleaned_data['localidad']                
                domicilio.calle = form.cleaned_data['calle']
                domicilio.numero = form.cleaned_data['numero']
                domicilio.aclaracion = form.cleaned_data['aclaracion']    
                domicilio.save()
            
            return render(request, 'carga_persona.html', {'title': 'Petición de Coca - PERSONAS', 'form': form, 'message': 'Sus datos fueron procesados con éxito.', 'button': 'CREAR PERSONA' })
        else:
            return render(request, "carga_persona.html", {'title': 'Petición de Coca - PERSONAS', 'form': form, 'message': 'Formulario no válido.', 'button': 'CREAR PERSONA' })

    return render(request, "carga_persona.html", {'title': 'Petición de Coca - PERSONAS', 'form': form, 'button': 'CREAR PERSONA'})

def edit_persona(request, individuo_id=None, num_doc=None):
    persona = Individuo.objects.get(pk=individuo_id)
    form = PersonaForm(instance=persona)
    domicilio = Domicilio.objects.filter(individuo_id=individuo_id, aislamiento = False).last() 
    if domicilio:
        form = PersonaForm(
                    instance = persona,
                    initial = {
                        'localidad': domicilio.localidad,                        
                        'calle': domicilio.calle,
                        'numero': domicilio.numero,
                        'aclaracion': domicilio.aclaracion,                                       
                }

        )   
    if request.method == 'POST':
        #Obtenemos peticion
        form = PersonaForm(request.POST, instance=persona)
        if form.is_valid():
            people = form.save(commit=False) 
            people.save()           
            #Grabamos modelos relacionados
            if form.cleaned_data['localidad']:                
                domicilio.individuo = persona
                domicilio.localidad = form.cleaned_data['localidad']                
                domicilio.calle = form.cleaned_data['calle']
                domicilio.numero = form.cleaned_data['numero']
                domicilio.aclaracion = form.cleaned_data['aclaracion']
                domicilio.save()                   
        else: 
            return render(request, "carga_persona.html", {'title': 'Petición de Coca - PERSONAS', 'form': form, 'message': 'Formulario no válido.', 'button': 'EDITAR PERSONA' })
        
        return render(request, "carga_persona.html", {'title': 'Petición de Coca - PERSONAS', 'form': form, 'message': 'Sus datos fueron modificados con éxito.', 'button': 'EDITAR PERSONA' })

    return render(request, "carga_persona.html", {'title': 'Petición de Coca - PERSONAS', 'form': form, 'button': 'EDITAR PERSONA'})

def disclaimer_orgedit(request, organization_id, cuit):
    organizacion = Organization.objects.get(pk=organization_id)
    form = OrganizationForm(instance=organizacion)
    domicilio = Domic_o.objects.get(organizacion_id=organizacion.id) 
    if domicilio:
        form = OrganizationForm(
                    instance = organizacion,
                    initial = {
                        'localidad': domicilio.localidad,
                        'barrio': domicilio.barrio,
                        'calle': domicilio.calle,
                        'numero': domicilio.numero,
                        'manzana': domicilio.manzana,
                        'lote': domicilio.lote,
                        'piso': domicilio.piso,                
                }

        )   
    if request.method == 'POST':
        #Obtenemos peticion
        form = OrganizationForm(request.POST, request.FILES, instance=organizacion)
        if form.is_valid():
            org = form.save(commit=False) 
            org.save()           
            #Grabamos modelos relacionados
            if form.cleaned_data['localidad']:                
                domicilio.organizacion = organizacion
                domicilio.localidad = form.cleaned_data['localidad']
                domicilio.barrio = form.cleaned_data['barrio'] 
                domicilio.calle = form.cleaned_data['calle']
                domicilio.numero = form.cleaned_data['numero']
                domicilio.manzana = form.cleaned_data['manzana']
                domicilio.lote = form.cleaned_data['lote']
                domicilio.piso = form.cleaned_data['piso']
                domicilio.save()                   
        else: 
            return render(request, "organizacion_peticion.html", {'title': 'Petición de Coca - ORGANIZACIONES', 'form': form, 'message': 'Formulario no valido.', 'button': 'EDITAR ORGANIZACION' })
        
        return render(request, "organizacion_peticion.html", {'title': 'Petición de Coca - ORGANIZACIONES', 'form': form, 'message': 'La organizacion fue modificada con éxito.', 'button': 'EDITAR ORGANIZACION' })

    return render(request, "organizacion_peticion.html", {'title': 'Petición de Coca - ORGANIZACIONES', 'form': form, 'button': 'EDITAR ORGANIZACION'})


def disclaimer_org(request, cuit=None):
    form = OrganizationForm(initial={"cuit": cuit})
    #Analizamos si mando informacion
    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            organizacion = form.save(commit=False)
            organizacion.save()
            #Creamos domicilio
            domicilio = Domic_o()
            domicilio.organizacion = organizacion
            if form.cleaned_data['localidad']:
                domicilio.localidad = form.cleaned_data['localidad']
                domicilio.barrio = form.cleaned_data['barrio']
                domicilio.calle = form.cleaned_data['calle']
                domicilio.numero = form.cleaned_data['numero']
                domicilio.manzana = form.cleaned_data['manzana']
                domicilio.lote = form.cleaned_data['lote']
                domicilio.piso = form.cleaned_data['piso']
                domicilio.save()
            
            return render(request, 'organizacion_peticion.html', {'title': 'Petición de Coca - ORGANIZACIONES', 'form': form, 'message': 'La organizacion fue CREADA con éxito.', 'button': 'CREAR ORGANIZACION' })
        else:
            return render(request, "organizacion_peticion.html", {'title': 'Petición de Coca - ORGANIZACIONES', 'form': form, 'message': 'Formulario no valido.', 'button': 'CREAR ORGANIZACION' })

    return render(request, "organizacion_peticion.html", {'title': 'Petición de Coca - ORGANIZACIONES', 'form': form, 'button': 'CREAR ORGANIZACION'})