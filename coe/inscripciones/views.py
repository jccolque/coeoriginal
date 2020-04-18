#imports de Python
import csv
#Imports de Django
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from coe.settings import SEND_MAIL
from core.forms import SearchForm
from core.functions import delete_tags
from informacion.models import Individuo
#Impors de la app
from .tokens import account_activation_token
from .choices import TIPO_DISPOSITIVO
from .models import Inscripto, Area, Tarea, TareaElegida, Dispositivo
from .forms import ProfesionalSaludForm, VoluntarioSocialForm
from .functions import actualizar_individuo

# Create your views here.
def inscripcion_salud(request):
    form = ProfesionalSaludForm()
    if request.method == "POST":
        try:#Tratamos de obtener el dni
            num_doc = request.POST['num_doc']
            individuo = Individuo.objects.get(num_doc=num_doc)
            if individuo.situacion_actual:
                if individuo.situacion_actual.conducta in ('D', 'E'):
                    return render(request, 'extras/error.html', {
                        'titulo': 'Inscripcion Denegada',
                        'error': "Usted se encuentra bajo Aislamiento, Contacte al Administrador.",
                    })
        except:
            individuo = None
        form = ProfesionalSaludForm(request.POST, request.FILES, instance=individuo)
        if form.is_valid():
            individuo = actualizar_individuo(form)
            #Armamos la inscripcion:
            inscripto = Inscripto()
            inscripto.tipo = 'PS'
            inscripto.individuo = individuo
            inscripto.profesion = form.cleaned_data['profesion']
            inscripto.matricula = form.cleaned_data['matricula']
            inscripto.archivo_dni = form.cleaned_data['archivo_dni']
            inscripto.archivo_titulo = form.cleaned_data['archivo_titulo']
            inscripto.info_extra = form.cleaned_data['info_extra']
            inscripto.save()
            #enviar email de validacion
            to_email = individuo.email
            #Preparamos el correo electronico
            mail_subject = 'Inscripcion al COE2020'
            message = render_to_string('emails/acc_active_inscripcion.html', {
                    'inscripto': inscripto,
                    'token':account_activation_token.make_token(inscripto),
                })
            #Instanciamos el objeto mail con destinatario
            email = EmailMessage(mail_subject, message, to=[to_email])
            #Enviamos el correo
            if SEND_MAIL:
                email.send()
            return render(request, 'inscripto_exito.html', {'inscripto': inscripto, })
    return render(request, "inscripcion_salud.html", {
        'titulo': "Inscribite",
        'form': form, 
        'boton': "Inscribirse",
    })

def inscripcion_social(request):
    dispositivos = TIPO_DISPOSITIVO
    areas = Area.objects.all()
    form = VoluntarioSocialForm()
    if request.method == "POST":
        try:#Tratamos de obtener el dni y el individuo
            num_doc = request.POST['num_doc']
            individuo = Individuo.objects.get(num_doc=num_doc)
            if individuo.situacion_actual:
                if individuo.situacion_actual.conducta in ('D', 'E'):
                    return render(request, 'extras/error.html', {
                        'titulo': 'Inscripcion Denegada',
                        'error': "Usted se encuentra bajo Aislamiento, Contacte al Administrador.",
                    })
        except:
            individuo = None
        form = VoluntarioSocialForm(request.POST, request.FILES, instance=individuo)
        if form.is_valid():
            #Obtenemos CheckBoxes
            tareas = request.POST.getlist('tareas')
            dispositivos = request.POST.getlist('dispositivos')
            #Actualizamos Individuo
            individuo = actualizar_individuo(form)
            #Creamos diccionario de tareas
            dict_tareas = {t.id:t for t in Tarea.objects.all()}
            #Armamos la inscripcion:
            inscripto = Inscripto()
            inscripto.tipo = 'VS'
            inscripto.individuo = individuo
            inscripto.oficio = form.cleaned_data['oficio']
            inscripto.archivo_dni = form.cleaned_data['archivo_dni']
            inscripto.grupo_sanguineo = form.cleaned_data['grupo_sanguineo']
            if 'dona_si' in form.cleaned_data:
                inscripto.dona_sangre = True
            inscripto.info_extra = form.cleaned_data['info_extra']
            #Agregamos las tareas
            if tareas:
                inscripto.save()
                for tarea in tareas:
                    teleg = TareaElegida(inscripto=inscripto)
                    teleg.tarea = dict_tareas[int(tarea)]
                    teleg.save()
                #Dispositivos
                for disp in dispositivos:
                    dispositivo = Dispositivo(inscripto=inscripto)
                    dispositivo.tipo = disp
                    dispositivo.save()
                #enviar email de validacion
                to_email = individuo.email
                #Preparamos el correo electronico
                mail_subject = 'Inscripcion al COE2020'
                message = render_to_string('emails/acc_active_inscripcion.html', {
                        'inscripto': inscripto,
                        'token':account_activation_token.make_token(inscripto),
                    })
                #Instanciamos el objeto mail con destinatario
                email = EmailMessage(mail_subject, message, to=[to_email])
                #Enviamos el correo
                if SEND_MAIL:
                    email.send()
                return render(request, 'inscripto_exito.html', {'inscripto': inscripto, })
            else:
                form.add_error("info_extra", "No ha Seleccionado ninguna tarea.")
    return render(request, "inscripcion_social.html", {
        'titulo': "Inscribite", 
        'form': form, 
        'boton': "Inscribirse",
        'areas': areas,
        'dispositivos': dispositivos,
    })

#Administracion
@permission_required('operadores.menu_inscripciones')
def menu(request):
    return render(request, 'menu_inscripciones.html', {})

@permission_required('operadores.menu_inscripciones')
def lista_voluntarios(request, tipo_inscripto):
    inscriptos = Inscripto.objects.filter(disponible=True, tipo_inscripto=tipo_inscripto)
    #Agregar buscador
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            inscriptos = inscriptos.filter(apellidos__icontains=search)
    return render(request, 'lista_inscripciones.html', {
        'inscriptos': inscriptos,
        'has_table': True,
    })

@permission_required('operadores.menu_inscripciones')
def ver_inscripto(request, inscripto_id=None):
    inscripto = Inscripto.objects.get(pk=inscripto_id)
    return render(request, 'ver_inscripto.html', {'inscripto': inscripto, })

@permission_required('operadores.menu_inscripciones')
def download_inscriptos(request):
    inscriptos = Inscripto.objects.all()
    #Iniciamos la creacion del csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Inscriptos.csv"'
    writer = csv.writer(response)
    writer.writerow(['REPORTE DE INSCRIPTOS'])
    writer.writerow(['FECHA:', timezone.now()])
    writer.writerow(['ID', 'TIPO_DOC', 'NUM_DOC', 'APELLIDOS', 'NOMBRES', 'PROFESION', 'MATRÍCULA', 'EMAIL', 'TELEFONO', 'INFO_EXTRA', 'VALIDO'])
    for item in inscriptos:
        writer.writerow([
            item.id,
            item.get_tipo_doc_display(),
            item.num_doc,
            item.apellidos,
            item.nombres,
            item.get_profesion_display(),
            item.matricula,
            item.email,
            item.telefono,
            delete_tags(item.info_extra),
            item.valido,
        ])
    #Enviamos el archivo para descargar
    return response

#Activar:
def activar_inscripcion_mail(request, inscripcion_id, token):
    try:
        inscripto = Inscripto.objects.get(pk=inscripcion_id)
    except(TypeError, ValueError, OverflowError, Inscripto.DoesNotExist):
        inscripto = None
    if inscripto and account_activation_token.check_token(inscripto, token):
        inscripto.valido = True
        try:
            inscripto.individuo = Individuo.objects.get(num_doc=inscripto.num_doc)
            #Actualizamos domicilio
        except Individuo.DoesNotExist:
            pass#No tenemos registrada a esa persona
        inscripto.save()
        texto = 'Excelente! Su correo electronico fue validada.'
    else:
        texto = 'El link de activacion es invalido!'
    return render(request, 'extras/resultado.html', {'texto': texto, })