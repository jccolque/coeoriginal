#Imports Python
from datetime import timedelta
#Imports Django
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
from django.core.mail import EmailMessage
#Imports del proyecto
from coe.settings import SEND_MAIL
from core.models import Aclaracion
from core.tokens import account_activation_token
from operadores.functions import obtener_operador
#Imports de la app
from .choices import TIPO_LLAMADA
from .models import Telefonista, Consulta, Respuesta, Llamada
from .models import DenunciaAnonima
from .forms import ConsultaForm, RespuestaForm, NuevoTelefonistaForm, LlamadaForm
from .forms import EvolucionarForm
from .functions import obtener_telefonista

#PUBLICO
#Consultas
def contacto(request):
    if request.method == 'POST': #En caso de que se haya realizado una busqueda
        consulta_form = ConsultaForm(request.POST)
        if consulta_form.is_valid():
            consulta = consulta_form.save()
            #enviar email de validacion
            if SEND_MAIL:
                to_email = consulta_form.cleaned_data.get('email')#Obtenemos el correo
                #Preparamos el correo electronico
                mail_subject = 'Confirma tu correo de respuesta por la Consultas Realizada al COE2020.'
                message = render_to_string('emails/acc_active_consulta.html', {
                        'consulta': consulta,
                        'token':account_activation_token.make_token(consulta),
                    })
                #Instanciamos el objeto mail con destinatario
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
            return render(request, 'contacto.html', {})
    else:
        consulta_form = ConsultaForm()
    return render(request, 'contacto.html', {"form": consulta_form,
                'titulo': "Envianos una consulta:", 'boton': "Enviar"})

def activar_consulta(request, consulta_id, token):
    try:
        consulta = Consulta.objects.get(pk=consulta_id)
    except(TypeError, ValueError, OverflowError, Consulta.DoesNotExist):
        consulta = None
    if consulta and account_activation_token.check_token(consulta, token):
        consulta.valida = True
        consulta.save()
        #Validado: La asignamos a un telefonista:
        telefonistas = Telefonista.objects.all().annotate(cantidad=Count('consultas'))
        for telefonista in telefonistas.order_by('cantidad'):
            if telefonista.max_pendientes > telefonista.cantidad:
                telefonista.consultas.add(consulta)
                break
        texto = 'Excelente! Su correo electronico fue asignado a uno de nuestro operadores.'
    else:
        texto = 'El link de activacion es invalido!'
    return render(request, 'extras/resultado.html', {'texto': texto, })

# Create your views here.
@permission_required('operadores.telefonistas')
def lista_denuncias(request, tipo=None, estado=None, telefonista_id=None):
    denuncias = DenunciaAnonima.objects.all()
    #Filtramos si es necesario
    if tipo:
        denuncias = denuncias.filter(tipo=tipo)
    if estado:
        denuncias = denuncias.filter(estado=estado)
    if telefonista_id:
        telefonista = Telefonista.objects.get(pk=telefonista_id)
        denuncias = denuncias.filter(aclaraciones__operador=telefonista.operador)
    #Si no hay filtros:
    if not tipo and not estado:
        denuncias = denuncias.exclude(estado__in=('RE','BA'))
    #Mostramos la lista
    return render(request, 'lista_denuncias.html', {
        'denuncias': denuncias,
        'has_table': True,
        'refresh': True,
    })

@permission_required('operadores.telefonistas')
def ver_denuncia(request, denuncia_id):
    denuncia = DenunciaAnonima.objects.get(pk=denuncia_id)
    return render(request, 'ver_denuncia.html', {
        'denuncia': denuncia,
    })

#Administrador
@permission_required('operadores.telefonistas')
def evolucionar_denuncia(request, denuncia_id):
    form = EvolucionarForm()
    if request.method == 'POST':
        form = EvolucionarForm(request.POST)
        if form.is_valid():
            denuncia = DenunciaAnonima.objects.get(pk=denuncia_id)
            #Creamos la aclaracion
            aclaracion = form.save(commit=False)
            aclaracion.modelo = 'DenunciaAnonima'
            aclaracion.operador = obtener_operador(request)
            aclaracion.save()
            #agregamos la aclaracion a la denuncia:
            denuncia.aclaraciones.add(aclaracion)
            denuncia.estado = form.cleaned_data['estado']
            #Una vez evolucionada la sacamos del telefonista:
            denuncia.telefonistas.clear()
            #Guardamos
            denuncia.save()
            return redirect('consultas:ver_denuncia', denuncia_id=denuncia.id)
    #Lanzamos form
    return render(request, "extras/generic_form.html", {'titulo': "Evolucionar Denuncia", 'form': form, 'boton': "Confirmar", })

@permission_required('operadores.telefonistas')
def eliminar_denuncia(request, denuncia_id):
    denuncia = DenunciaAnonima.objects.get(pk=denuncia_id)
    if request.method == "POST":
        #Creamos aclaracion
        aclaracion = Aclaracion()
        aclaracion.operador = obtener_operador(request)
        aclaracion.descripcion = "Se elimino la Denuncia"
        aclaracion.save()
        #modificamos denuncia
        denuncia.aclaraciones.add(aclaracion)
        denuncia.estado = 'BA'
        denuncia.save()
        return redirect('consultas:lista_denuncias')
    return render(request, "extras/confirmar.html", {
            'titulo': "Eliminar Denuncia",
            'message': "Si realiza esta accion quedara registrada por su usuario.",
            'has_form': True,
        }
    )

#Administracion Consultas
@permission_required('operadores.telefonistas')
def menu(request):
    return render(request, 'menu_consultas.html', {
        'es_telefonista': Telefonista.objects.filter(operador=obtener_operador(request)).exists(),
    })

@permission_required('operadores.admin_telefonistas')
def lista_consultas(request, telefonista_id=None):
    if telefonista_id:
        telefonista = Telefonista.objects.get(pk=telefonista_id)
        consultas = Consulta.objects.filter(respuestas__telefonista=telefonista)
    else:#Lista abierta
        consultas = Consulta.objects.filter(valida=True, respondida=False)
    #Mostramos consultas
    return render(request, 'lista_consultas.html', {
        "consultas": consultas, 
        "has_table": True,
        "refresh": True,
    })

@permission_required('operadores.admin_telefonistas')
def lista_respondidas(request):
    consultas = Consulta.objects.filter(respondida=True)
    return render(request, 'lista_respondidas.html', {
        "consultas": consultas,
        "has_table": True,
    })

@permission_required('operadores.telefonistas')
def ver_consulta(request, consulta_id):
    form = RespuestaForm()
    consulta = Consulta.objects.get(pk=consulta_id)
    if request.method == "POST":
        form = RespuestaForm(request.POST)
        if form.is_valid():
            #Preparamos el objeto respuesta
            respuesta = form.save(commit=False)
            respuesta.consulta = consulta
            #enviar email de respuesta
            if SEND_MAIL:
                to_email = consulta.email
                #Preparamos el correo electronico
                mail_subject = 'COE2020: Respondimos tu Consulta ' + consulta.asunto
                message = render_to_string('emails/respuesta_consulta.html', {
                        'consulta': consulta,
                        'respuesta':respuesta,
                    })
                #Instanciamos el objeto mail con destinatario
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
            #La marcamos como respondida
            consulta.respondida = True
            try:
                respuesta.telefonista = obtener_telefonista(request)
                respuesta.telefonista.consultas.remove(consulta)
            except:
                pass#No la respondio un telefonista/sin asignar
            #Guardamos
            consulta.save()
            return redirect('consultas:lista_consultas')
    return render(request, 'ver_consulta.html', {"consulta": consulta, 'form': form, })

@permission_required('operadores.telefonistas')
def consulta_respondida(request, consulta_id):
    consulta = Consulta.objects.get(pk=consulta_id)
    consulta.respondida = True
    consulta.save()
    #Chequeamos si es telefonista:
    telefonista = obtener_telefonista(request)
    if telefonista:
        #Generamos respuesta automatica:
        respuesta = Respuesta(consulta=consulta)
        respuesta.telefonista = telefonista
        respuesta.respuesta = "Marcada como respondida a travez del boton."
        respuesta.save()
        #La quitamos del panel:
        telefonista.consultas.remove(consulta)
        #Permitimos cargar llamada:
        return redirect('consultas:cargar_llamada_consulta', telefonista_id=telefonista.id, consulta_id=consulta.id)
    return render(request, "extras/close.html")

#Telefonista
@permission_required('operadores.admin_telefonistas')
def lista_telefonistas(request, telefonista_id=None):
    telefonistas = Telefonista.objects.all()
    telefonistas = telefonistas.select_related('operador', 'operador__usuario')
    #Lanzamos listado
    return render(request, "lista_telefonistas.html", {
        'telefonistas': telefonistas,
        'has_table': True,
    })

@permission_required('operadores.admin_telefonistas')
def informe_actividad(request, telefonista_id=None):
    #obtenemos informacion
    telefonistas = Telefonista.objects.all()
    llamadas = Llamada.objects.all()
    consultas = Consulta.objects.all()
    if telefonista_id:
        telefonistas = telefonistas.filter(pk=telefonista_id)
        llamadas = llamadas.filter(telefonista__pk=telefonista_id)
        consultas = consultas.filter(Q(respuestas__telefonista__pk=telefonista_id) | Q(telefonista__pk=telefonista_id)).distinct()
    #Generamos informacion:
    #llamadas
    data_llamadas = []
    for tipo in TIPO_LLAMADA:
        data_llamadas.append(
            [
                tipo[1],
                llamadas.filter(tipo=tipo[0], fecha__gt=timezone.now() - timedelta(hours=24)).count(),
                llamadas.filter(tipo=tipo[0], fecha__gt=timezone.now() - timedelta(hours=24 * 7)).count(),
                llamadas.filter(tipo=tipo[0]).count(),
            ]
        )

    graf_llamadas = None #PROCESAR!
    #consultas
    data_consultas = []
    data_consultas.append(
        [
            'Recibidas Totales',
            consultas.filter(fecha_consulta__gt=timezone.now() - timedelta(hours=24)).count(),
            consultas.filter(fecha_consulta__gt=timezone.now() - timedelta(hours=24 * 7)).count(),
            consultas.count(),
        ]
    )
    data_consultas.append(
        [
            'Recibidas Validas',
            consultas.filter(valida=True, fecha_consulta__gt=timezone.now() - timedelta(hours=24)).count(),
            consultas.filter(valida=True, fecha_consulta__gt=timezone.now() - timedelta(hours=24 * 7)).count(),
            consultas.filter(valida=True).count(),
        ]
    )
    data_consultas.append(
        [
            'Respondidas',
            consultas.filter(respondida=True, fecha_consulta__gt=timezone.now() - timedelta(hours=24)).count(),
            consultas.filter(respondida=True, fecha_consulta__gt=timezone.now() - timedelta(hours=24 * 7)).count(),
            consultas.filter(respondida=True).count(),
        ]
    )
    graf_consultas = None #PROCESAR!
    #Lanzamos reporte
    return render(request, "informe_actividad.html", {
        'telefonistas': telefonistas,
        'has_table': True,
        'llamadas': data_llamadas,
        'consultas': data_consultas,
    })

@permission_required('operadores.admin_telefonistas')
def agregar_telefonista(request, telefonista_id=None):
    telefonista = None
    if telefonista_id:
        telefonista = Telefonista.objects.get(pk=telefonista_id)
    form = NuevoTelefonistaForm(instance=telefonista)
    if request.method == "POST":
        form = NuevoTelefonistaForm(request.POST, instance=telefonista)
        if form.is_valid():
            form.save()
            return redirect('consultas:lista_telefonistas')
    return render(request, "extras/generic_form.html", {'titulo': "Habilitar Nuevo Telefonista", 'form': form, 'boton': "Habilitar", })

@permission_required('operadores.admin_telefonistas')
def del_telefonista(request, telefonista_id):
    telefonista = Telefonista.objects.get(pk=telefonista_id)
    if request.method == "POST":
        telefonista.delete()
        return redirect('consultas:lista_telefonistas')
    return render(request, "extras/confirmar.html", {
            'titulo': "Eliminar Telefonista",
            'message': "Todas las operaciones realizadas quedaran sin registro de quien las atendio.",
            'has_form': True,
        }
    )

@permission_required('operadores.admin_telefonistas')
def lista_llamadas(request, telefonista_id=None):
    llamadas = Llamada.objects.all()
    if telefonista_id:
        telefonista = Telefonista.objects.get(pk=telefonista_id)
        llamadas = llamadas.filter(telefonista=telefonista)
    #Mostramos:
    return render(request, "lista_llamadas.html", {
        'llamadas': llamadas,
        'has_table': True,
    })

#PANEL:
@permission_required('operadores.telefonistas')
def ver_panel(request, telefonista_id=None):
    #Obtenemos el telefonista
    if telefonista_id:
        telefonista = Telefonista.objects.get(pk=telefonista_id)
    else:#Si no se ingreso con un id de telefonista:
        operador = obtener_operador(request)
        try:
            telefonista = operador.telefonista
        except:
            return render(request, 'extras/error.html', {
            'titulo': 'No existe Panel de Telefonista',
            'error': "Usted no es un Telefonista Habilitado, si deberia tener acceso a esta seccion, por favor contacte a los administradores.",
        })
    #Obtenemos llamadas y consultas respondidas
    llamadas = Llamada.objects.filter(telefonista=telefonista)
    respuestas = Respuesta.objects.filter(telefonista=telefonista)
    denuncias = DenunciaAnonima.objects.filter(aclaraciones__operador=telefonista.operador).distinct()
    #Mostramos panel
    return render(request, "panel_telefonista.html", {
        'telefonista': telefonista,
        'llamadas': llamadas,
        'respuestas': respuestas,
        'denuncias': denuncias,
        'refresh': True,
        'has_table': True,
    })

#llamadas
@permission_required('operadores.telefonistas')
def cargar_llamada(request, telefonista_id, llamada_id=None, consulta_id=None):
    #Obtenemos datos base
    telefonista = Telefonista.objects.get(pk=telefonista_id)
    llamada = None
    if llamada_id:
        llamada = Llamada.objects.get(pk=llamada_id)
    consulta = None
    if consulta_id:
        consulta = Consulta.objects.get(pk=consulta_id)
    #Generamos Form
    form = LlamadaForm(instance=llamada)
    if request.method == "POST":
        form = LlamadaForm(request.POST, instance=llamada)
        if form.is_valid():
            llamada = form.save(commit=False)
            llamada.telefonista = telefonista
            llamada.save()
            return render(request, "extras/close.html")
    return render(request, "cargar_llamada.html", {
        'titulo': "Cargar Llamada Telefonica",
        'form': form,
        'consulta': consulta,
        'boton': "Procesar",
    })

@permission_required('operadores.admin_telefonistas')
def del_llamada(request, llamada_id):
    #Obtenemos info
    llamada = Llamada.objects.get(pk=llamada_id)
    telefonista = llamada.telefonista
    #La eliminamos
    llamada.delete()
    #Volvemos a la lista
    return redirect('consultas:lista_llamadas', telefonista_id=telefonista.pk)
