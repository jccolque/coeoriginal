#Imports Django
from datetime import datetime, timedelta, time
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
#Imports del proyecto
from coe.settings import GEOPOSITION_GOOGLE_MAPS_API_KEY
from coe.constantes import DIAS_CUARENTENA
from core.decoradores import superuser_required
from core.functions import date2str
from core.forms import SearchForm, FileForm, JustificarForm, TextoForm, ChangeEmailForm
from georef.models import Nacionalidad, Ubicacion
from georef.functions import obtener_argentina
from seguimiento.models import Seguimiento
from operadores.functions import obtener_operador
from background.functions import crear_progress_link
from graficos.functions import obtener_grafico
from app.models import AppData
from permisos.forms import FotoForm
from geotracking.models import GeoPosicion
from seguimiento.choices import TIPO_VIGIA
from seguimiento.functions import asignar_vigilante
#imports de la app
from .choices import TIPO_ESTADO, TIPO_CONDUCTA
from .choices import TIPO_ATRIBUTO, TIPO_SINTOMA
from .models import Archivo
from .models import Vehiculo, TrasladoVehiculo#, Pasajero
from .models import Individuo, SignosVitales, Relacion
from .models import Situacion
from .models import Domicilio
from .models import Atributo, Sintoma, Patologia
from .models import Documento
from .forms import ArchivoForm, ArchivoFormWithPass
from .forms import VehiculoForm, TrasladoVehiculoForm
from .forms import IndividuoForm, FullIndividuoForm, InquilinoForm, MinIndividuoForm
from .forms import NumDocForm
from .forms import BuscadorIndividuosForm, TrasladarIndividuoForm
from .forms import DomicilioForm, AtributoForm, SintomaForm, PatologiaForm
from .forms import SituacionForm, RelacionForm
from .forms import SearchIndividuoForm, SearchVehiculoForm
from .forms import DocumentoForm, SignosVitalesForm
from .forms import ReporteHotelesForm
from .upload_tasks import guardar_same, guardar_epidemiologia
from .upload_tasks import guardar_padron_individuos, guardar_padron_domicilios
from .functions import obtener_relacionados

#Administrar
@permission_required('operadores.menu_informacion')
def menu(request):
    return render(request, 'menu_informacion.html', {})

#ARCHIVOS
@permission_required('operadores.archivos')
def archivos_pendientes(request, procesado=None):
    form = SearchForm()
    archivos = Archivo.objects.all()
    #Si busco, filtramos
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            archivos = archivos.filter(nombre__icontains=search)
    else:#Si no busco traemos segun corresponda
        if procesado:
            archivos = archivos.filter(procesado=True)
        else: 
            archivos = archivos.filter(procesado=False)
    return render(request, 'archivos_pendientes.html', {
        'archivos': archivos,
        'has_table': True,
    })

@permission_required('operadores.archivos')
def ver_archivo(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id)
    return render(request, 'ver_archivo.html', {'archivo': archivo,})

@permission_required('operadores.archivos')
def upload_archivos(request):
    form = ArchivoForm()
    if request.method == "POST":
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.save()
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Subir Archivo para Carga", 'form': form, 'boton': "Subir", })

@permission_required('operadores.archivos')
def procesar_archivos(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id)
    archivo.procesado = not archivo.procesado
    archivo.save()
    return redirect('informacion:ver_archivo', archivo_id=archivo.id)

#VEHICULOS
@permission_required('operadores.vehiculos')
def buscar_vehiculo(request):
    form = SearchVehiculoForm()
    if request.method == "POST":
        form = SearchVehiculoForm(request.POST)
        if form.is_valid():
            identificacion = form.cleaned_data['identificacion']
            try:
                vehiculo = Vehiculo.objects.get(identificacion=identificacion)
                return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
            except Vehiculo.DoesNotExist:
                return redirect('informacion:cargar_vehiculo', identificacion=identificacion)
    return render(request, "extras/generic_form.html", {'titulo': "Buscar Vehiculo", 'form': form, 'boton': "Buscar", })

@permission_required('operadores.vehiculos')
def listar_vehiculos(request, tipo_id=None):
    vehiculos = Vehiculo.objects.all()
    if tipo_id:
        vehiculos = vehiculos.filter(tipo=tipo_id)
    return render(request, "lista_vehiculos.html", {
        'vehiculos': vehiculos,    
        'has_table': True,
    })

@permission_required('operadores.vehiculos')
def ver_vehiculo(request, vehiculo_id):
    vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    return render(request, "ver_vehiculo.html", {'vehiculo': vehiculo, })

@permission_required('operadores.vehiculos')
def cargar_vehiculo(request, vehiculo_id=None, identificacion=None):
    vehiculo = None
    if vehiculo_id:
        vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    else:
        vehiculo = Vehiculo(identificacion=identificacion)
    #Cargamos Form Inicial
    form = VehiculoForm(instance=vehiculo,)
    if request.method == "POST":
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            operador = obtener_operador(request)
            vehiculo = form.save(commit=False)
            vehiculo.save()
            return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Vehiculo", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.vehiculos')
def cargar_traslado(request, vehiculo_id):
    vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    form = TrasladoVehiculoForm()
    if request.method == "POST":
        form = TrasladoVehiculoForm(request.POST)
        if form.is_valid():
            traslado = form.save(commit=False)
            traslado.vehiculo = vehiculo
            form.save()
            return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Traslado Vehicular", 'form': form, 'boton': "Cargar", }) 

#INDIVIDUOS
@permission_required('operadores.individuos')
def buscar_individuo(request, traslado_id=None):
    form = SearchIndividuoForm()
    if request.method == "POST":
        form = SearchIndividuoForm(request.POST)
        if form.is_valid():
            num_doc = form.cleaned_data['num_doc'].upper()
            try:
                individuo = Individuo.objects.get(num_doc=num_doc)
                if traslado_id:#lo cargamos en el vehiculo y volvemos al vehiculo:
                    traslado = TrasladoVehiculo.objects.get(pk=traslado_id)
                    traslado.pasajeros.add(individuo)
                    return redirect('informacion:ver_vehiculo', vehiculo_id=traslado.vehiculo.id)
                else:#Se va a la planilla simplemente
                    return redirect('informacion:ver_individuo', individuo_id=individuo.id)
            except Individuo.DoesNotExist:
                if traslado_id:#Se carga en un vehiculo:
                    return redirect('informacion:cargar_pasajero_nuevo', num_doc=num_doc, traslado_id=traslado_id)
                else:
                    return redirect('informacion:cargar_individuo', num_doc=num_doc)
    return render(request, "extras/generic_form.html", {'titulo': "Indicar Documento de Individuo", 'form': form, 'boton': "Buscar", })

@permission_required('operadores.individuos')
def cargar_individuo(request, traslado_id=None, num_doc=None):
    form = FullIndividuoForm(initial={"num_doc":num_doc})
    #Analizamos si mando informacion:
    if request.method == "POST":
        form = FullIndividuoForm(request.POST)
        if form.is_valid():
            operador = obtener_operador(request)
            individuo = form.save(commit=False)
            #Le cargamos el ultimo domicilio y situacion
            if not individuo.situacion_actual:
                individuo.situacion_actual = individuo.situaciones.last()
            if not individuo.domicilio_actual:
                individuo.domicilio_actual = individuo.domicilios.last()
            individuo.save()
            #Generamos modelos externos:
            if form.cleaned_data['dom_localidad']:
                domicilio = Domicilio()
                domicilio.individuo = individuo
                domicilio.localidad = form.cleaned_data['dom_localidad']
                domicilio.calle = form.cleaned_data['dom_calle']
                domicilio.numero = form.cleaned_data['dom_numero']
                domicilio.aclaracion = form.cleaned_data['dom_aclaracion']
            #Si cambio el domicilio Actual:
                if not individuo.domicilio_actual:
                    domicilio.save()
                else:
                    Domicilio.objects.bulk_create([domicilio, ])
            #Creamos atributos
            atributos = form.cleaned_data['atributos']
            individuo.atributos.all().delete()
            for atributo_id in atributos:
                atributo = Atributo()
                atributo.individuo = individuo
                atributo.tipo = atributo_id
                atributo.save()           
            #Creamos sintomas
            sintomas = form.cleaned_data['sintomas']
            individuo.sintomas.all().delete()
            for sintoma_id in sintomas:
                sintoma = Sintoma()
                sintoma.individuo = individuo
                sintoma.tipo = sintoma_id
                sintoma.save()  
            #Si vino en un vehiculo
            if traslado_id:
                traslado = TrasladoVehiculo.objects.get(pk=traslado_id)
                traslado.pasajeros.add(individuo)
                return redirect('informacion:ver_vehiculo', vehiculo_id=traslado.vehiculo.id)
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "cargar_individuo.html", {'titulo': "Cargar Individuo", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def mod_individuo(request, individuo_id, num_doc):
    individuo = Individuo.objects.get(pk=individuo_id, num_doc=num_doc)
    form = IndividuoForm(instance=individuo)
    if request.method == 'POST':
        form = IndividuoForm(request.POST, instance=individuo)
        if form.is_valid():
            form.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Modificar Individuo", 'form': form, 'boton': "Modificar", })

@permission_required('operadores.individuos')
def cargar_fotografia(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = FotoForm()
    if request.method == "POST":
        form = FotoForm(request.POST, request.FILES)
        if form.is_valid():
            individuo.fotografia = form.cleaned_data['fotografia']
            individuo.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Subir Fotografia", 'form': form, 'boton': "Cargar", })

#Aislamiento Manual
@permission_required('operadores.individuos')
def buscar_inquilino(request, ubicacion_id):
    form = SearchIndividuoForm()
    if request.method == "POST":
        form = SearchIndividuoForm(request.POST)
        if form.is_valid():
            num_doc = form.cleaned_data['num_doc'].upper()
            try:
                individuo = Individuo.objects.get(num_doc=num_doc)
                return redirect('informacion:confirmar_inquilino', ubicacion_id=ubicacion_id, individuo_id=individuo.id)
            except Individuo.DoesNotExist:
                return redirect('informacion:cargar_inquilino', ubicacion_id=ubicacion_id, num_doc=num_doc)
    return render(request, "extras/generic_form.html", {'titulo': "Trasladar Individuo", 'form': form, 'boton': "Trasladar", })

@permission_required('operadores.individuos')
def confirmar_inquilino(request, ubicacion_id, individuo_id):
    form = TrasladarIndividuoForm()
    ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
    individuo = Individuo.objects.get(pk=individuo_id)
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            form = TrasladarIndividuoForm(request.POST)
            if form.is_valid():
                domicilio = Domicilio(individuo=individuo)
                domicilio.localidad = ubicacion.localidad
                domicilio.calle = ubicacion.calle
                domicilio.numero = ubicacion.numero
                domicilio.aclaracion = ubicacion.nombre + " Habitacion:" + form.cleaned_data['habitacion']
                domicilio.fecha = datetime.combine(form.cleaned_data['fecha'].date(), time(6,0))#Horario Fijo
                #domicilio.aislamiento = True
                domicilio.tipo = ubicacion.tipo
                domicilio.ubicacion = ubicacion
                domicilio.save()
                #Creamos Cronologia
                seguimiento = Seguimiento(individuo=individuo)
                seguimiento.tipo = 'TA'
                seguimiento.aclaracion = ubicacion.nombre + " (Traslado Via Sistema)"
                seguimiento.fecha = form.cleaned_data['fecha']
                seguimiento.save()
                return redirect('georef:ver_ubicacion', ubicacion_id=ubicacion.id)
        else:
            return redirect('informacion:buscar_inquilino', ubicacion_id=ubicacion.id)
    #Mostramos form
    return render(request, 'confirmar_inquilino.html', 
            {
                'form': form,
                'ubicacion': ubicacion,
                'individuo': individuo,
            }
        )

@permission_required('operadores.individuos')
def cargar_inquilino(request, ubicacion_id, num_doc):
    ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
    form = InquilinoForm(initial=
        {
            'num_doc': num_doc,
            'ubicacion': ubicacion,
        }
    )
    #Si nos mando el individuo completo lo creamos e ingresamos
    if request.method == 'POST':
        form = InquilinoForm(request.POST)
        if form.is_valid():
            #Creamos el individuo
            individuo = form.save(commit=False)
            individuo.save()
            #Obtenemos la ubicacion
            ubicacion = form.cleaned_data['ubicacion']
            #Generamos modelos externos:
            #Creamos atributos
            atributos = form.cleaned_data['atributos']
            individuo.atributos.all().delete()
            for atributo_id in atributos:
                atributo = Atributo()
                atributo.individuo = individuo
                atributo.tipo = atributo_id
                atributo.save()           
            #Creamos sintomas
            sintomas = form.cleaned_data['sintomas']
            individuo.sintomas.all().delete()
            for sintoma_id in sintomas:
                sintoma = Sintoma()
                sintoma.individuo = individuo
                sintoma.tipo = sintoma_id
                sintoma.save()  
            #Creamos nuevo domicilio:
            domicilio = Domicilio(individuo=individuo)
            domicilio.localidad = ubicacion.localidad
            domicilio.calle = ubicacion.calle
            domicilio.numero = ubicacion.numero
            domicilio.aclaracion = ubicacion.nombre + " (Traslado Via Sistema)"
            #domicilio.aislamiento = True
            domicilio.tipo = ubicacion.tipo
            domicilio.ubicacion = ubicacion
            domicilio.fecha = form.cleaned_data['fecha']
            domicilio.save()
            #Creamos Cronologia
            seguimiento = Seguimiento(individuo=individuo)
            seguimiento.tipo = 'TA'
            seguimiento.aclaracion = ubicacion.nombre +' | '+ form.cleaned_data['habitacion']
            seguimiento.fecha = form.cleaned_data['fecha']
            seguimiento.save()
            #Volvemos al aislamiento
            return redirect('georef:ver_ubicacion', ubicacion_id=ubicacion.id)
    #Lanzamos formulario
    return render(request, "cargar_inquilino.html",
        {
            'titulo': "Cargar Inquilino",
            'form': form, 
            'boton': "Cargar",
            'ubicacion': ubicacion,
        }
    )

@permission_required('operadores.individuos')
def cargar_min_individuo(request):
    form = MinIndividuoForm()
    if request.method == "POST":
        form = MinIndividuoForm(request.POST)
        if form.is_valid():
            individuo = form.save(commit=False)
            individuo.nacionalidad = obtener_argentina()
            form.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Individuo", 'form': form, 'boton': "Cargar", }) 


#INDIVIDUOS
@permission_required('operadores.individuos')
def ver_individuo(request, individuo_id):
    #Optimizamos la busqueda
    individuo = Individuo.objects.prefetch_related(
        'domicilios', 'domicilios__localidad', 'domicilios__localidad__departamento',
        'geoposiciones',
        'signos_vitales',
        'seguimientos', 'seguimientos__operador',
        'atributos',
        'sintomas',
        'patologias',
        'documentos',
        'situaciones',
        'relaciones',
        'relaciones__relacionado',
        'relaciones__relacionado__situacion_actual',
        'traslados', 'traslados__vehiculo',
        'llamadas', 'llamadas__telefonista', 'llamadas__telefonista__operador',
        'voluntariados')
    individuo = individuo.select_related(
        'situacion_actual', 
        'domicilio_actual',
        'condicion',
        'appdata',
        'origen_internacional', 'origen_nacional',
        'destino')
    individuo = individuo.get(pk=individuo_id)
    #Chequeamos que no sea info confidencial
    sit = individuo.get_situacion()
    if sit.estado == 50:
        #Si es Confirmado y no se tiene permisos
        if not request.user.has_perm('operadores.epidemiologia') and not individuo.vigiladores.filter(operador=obtener_operador(request)).exists():        
            return render(request, 'extras/error.html', {
                'titulo': 'Informacion Confidencial',
                'error': "Usted no tiene acceso a este inidividuo.",
            })
    #Mostrmoas individuo
    return render(request, "ver_individuo.html", {'individuo': individuo, })

#Relaciones
@permission_required('operadores.individuos')
def arbol_relaciones(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    set_relaciones = obtener_relacionados(individuo, set())
    #Podriamos hacer un dict con todos los select related y prefetchs para optimizar
    return render(request, "arbol/arbol_relaciones.html", {
        'individuo': individuo, 
        'set_relaciones': set_relaciones,
        'ancho': 15000,
    })

#Individuos
@permission_required('operadores.individuos')
def buscador_individuos(request):
    form = BuscadorIndividuosForm()
    if request.method == "POST":
        form = BuscadorIndividuosForm(request.POST)
        if form.is_valid():
            #Tramos todos los individuos:
            individuos = Individuo.objects.all()
            #Aplicamos los filtros
            if form.cleaned_data['nombre']:
                individuos = individuos.filter(nombres__icontains=form.cleaned_data['nombre'])
            if  form.cleaned_data['apellido']:
                individuos = individuos.filter(apellidos__icontains=form.cleaned_data['apellido'])
            if form.cleaned_data['calle']:
                individuos = individuos.filter(domicilios__calle__icontains=form.cleaned_data['calle'])
            if form.cleaned_data['localidad']:
                individuos = individuos.filter(domicilios__localidad=form.cleaned_data['localidad'])
            #Optimizamos las busquedas a la db
            individuos = individuos.select_related('nacionalidad', 'origen_internacional', 'origen_nacional', 'destino', )
            individuos = individuos.select_related('situacion_actual', 'domicilio_actual', 'domicilio_actual__localidad')
            individuos = individuos.prefetch_related('atributos', 'sintomas', 'situaciones', 'relaciones')
            individuos = individuos.prefetch_related('atributos', 'sintomas')
            individuos = individuos.prefetch_related('domicilios')
            #Mandamos el listado
            return render(request, "lista_individuos.html", {
                'individuos': individuos,
                'has_table': True,
            })
    return render(request, "extras/generic_form.html", {'titulo': "Buscador de Individuos", 'form': form, 'boton': "Buscar", })

#Listas:
@permission_required('operadores.individuos')
def lista_individuos(
        request,
        nacionalidad_id=None,
        estado=None,
        conducta=None
    ):
    #Filtramos segun corresponda
    if nacionalidad_id:
        individuos = Individuo.objects.filter(nacionalidad__id=nacionalidad_id)
    elif estado:
        individuos = Individuo.objects.filter(situacion_actual__estado=estado)
    elif conducta:
        individuos = Individuo.objects.filter(situacion_actual__conducta=conducta)
    #Optimizamos
    individuos = individuos.select_related('nacionalidad', 'origen_internacional', 'origen_nacional', 'destino', )
    individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__localidad', 'domicilio_actual__localidad__departamento')
    individuos = individuos.select_related('situacion_actual')
    individuos = individuos.prefetch_related('atributos', 'sintomas', 'situaciones', 'relaciones')
    #Chequeamos que no sea info confidencial:
    if estado == 50 and not request.user.has_perm('operadores.epidemiologia'):
        return render(request, 'extras/error.html', {
            'titulo': 'Informacion Confidencial',
            'error': "Usted no tiene acceso a este listado.",
        })
    #Mostramos lista
    return render(request, "lista_individuos.html", {
        'individuos': individuos,
        'has_table': True,
    })

#CARGA DE ELEMENTOS
@permission_required('operadores.individuos')
def mod_num_doc(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = NumDocForm(instance=individuo)
    if request.method == 'POST':
        form = NumDocForm(request.POST, instance=individuo)
        if form.is_valid():
            form.save()
            #Cerramos ventana
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cambiar Documento", 'form': form, 'boton': "Modificar", })    

#Modificar Telefono
@permission_required('operadores.individuos')
def mod_telefono(request, individuo_id=None):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = TextoForm(initial={'texto':individuo.telefono})
    if request.method == 'POST':
        form = TextoForm(request.POST)
        if form.is_valid():
            individuo.telefono = form.cleaned_data['texto']
            individuo.save()
            #Vemos si fue descartado de vigilancia por falta de telefono
            if individuo.seguimientos.filter(tipo='TE').exists():
                #Le eliminamos la flag de telefono errado
                individuo.seguimientos.filter(tipo='TE').delete()
                #Devolvemos todas las vigilancias no vencidas:
                limite = timezone.now() - timedelta(days=DIAS_CUARENTENA)
                tipos_de_vigia = [t[0] for t in TIPO_VIGIA]
                for vigilancia in individuo.atributos.filter(tipo__in=tipos_de_vigia, fecha__gt=limite):
                    asignar_vigilante(individuo, vigilancia.tipo)
            #Cerramos ventana
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cambiar Telefono a "+str(individuo), 'form': form, 'boton': "Modificar", })

#Modificar Email
@permission_required('operadores.individuos')
def mod_email(request, individuo_id=None):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = ChangeEmailForm(initial={'email':individuo.email})
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            individuo.email = form.cleaned_data['email']
            individuo.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cambiar Email", 'form': form, 'boton': "Modificar", })

#Domicilio
@permission_required('operadores.individuos')
def cargar_domicilio(request, individuo_id=None, domicilio_id=None):
    domicilio = None
    if individuo_id:
        individuo = Individuo.objects.get(pk=individuo_id)
    if domicilio_id:
        domicilio = Domicilio.objects.get(pk=domicilio_id)
        individuo = domicilio.individuo
        domicilio.fecha = timezone.now()#le renovamos la fecha
    #Cargamos formulario
    form = DomicilioForm(instance=domicilio)
    if request.method == "POST":
        form = DomicilioForm(request.POST, instance=domicilio)
        if form.is_valid():
            domicilio = form.save(commit=False)
            domicilio.individuo = individuo
            if domicilio.pk:#Se chequea que no sea una modificacion
                domicilio.save()
            else:#Si es nuevo lo creamos via bulk para que no cambie el dom actual:
                Domicilio.objects.bulk_create([domicilio,])
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Domicilio", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def volver_domicilio(request, domicilio_id):
    nuevo_domicilio = Domicilio.objects.get(pk=domicilio_id)
    nuevo_domicilio.pk = None
    if nuevo_domicilio.ubicacion:
        nuevo_domicilio.aclaracion = "Devuelto a " + nuevo_domicilio.ubicacion.nombre + " por " + str(obtener_operador(request))
    else:
        nuevo_domicilio.aclaracion = "Devuelto a Hogar por " + str(obtener_operador(request))
    nuevo_domicilio.fecha = timezone.now()
    nuevo_domicilio.save()
    return redirect('informacion:ver_individuo', individuo_id=nuevo_domicilio.individuo.id)

@permission_required('operadores.individuos')
def del_domicilio(request, domicilio_id=None):
    domicilio = Domicilio.objects.get(pk=domicilio_id)
    individuo = domicilio.individuo
    if domicilio == individuo.domicilio_actual:
        return render(request, 'extras/error.html', {
            'titulo': 'Eliminar Domicilio',
            'error': "No se puede Borrar el domicilio Actual.",
        })
    else:
        domicilio.delete()
        return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Traslados
@permission_required('operadores.individuos')
def elegir_ubicacion(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    #Obtenemos y optimizamos ubicaciones
    ubicaciones = Ubicacion.objects.filter(tipo__in=('AI', 'IN'))
    ubicaciones = ubicaciones.select_related('localidad')
    ubicaciones = ubicaciones.prefetch_related('aislados', 'aislados__ubicacion')
    #Mostramos lista
    return render(request, "seleccionar_ubicacion.html", {
        'individuo': individuo,
        'ubicaciones': ubicaciones,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def elegir_vehiculo(request, individuo_id, ubicacion_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
    vehiculos = Vehiculo.objects.filter(
        tipo=1,
    )
    return render(request, "seleccionar_vehiculo.html", {
        'individuo': individuo,
        'ubicacion': ubicacion,
        'vehiculos': vehiculos,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def trasladar(request, individuo_id, ubicacion_id, vehiculo_id):
    #Obtenemos lo importante
    individuo = Individuo.objects.get(pk=individuo_id)
    ubicacion = Ubicacion.objects.get(pk=ubicacion_id)
    vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    #Creamos nuevo domicilio:
    domicilio = Domicilio(individuo=individuo)
    domicilio.tipo = ubicacion.tipo
    domicilio.calle = ubicacion.calle
    domicilio.numero = ubicacion.numero
    domicilio.aclaracion = ubicacion.nombre + " (Traslado Via Sistema)"
    domicilio.localidad = ubicacion.localidad
    #domicilio.aislamiento = True
    domicilio.tipo = ubicacion.tipo
    domicilio.ubicacion = ubicacion
    domicilio.save()
    #Creamos Cronologia
    seguimiento = Seguimiento(individuo=individuo)
    seguimiento.tipo = 'C'
    seguimiento.aclaracion = ubicacion.nombre + " (Traslado Via Sistema)"
    seguimiento.save()
    #Creamos Traslado en el vehiculo
    traslado = TrasladoVehiculo(vehiculo=vehiculo)
    traslado.aclaracion = ubicacion.nombre + " (Traslado Via Sistema)"
    traslado.save()
    traslado.pasajeros.add(individuo)
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Situacion
@permission_required('operadores.individuos')
def cargar_situacion(request, individuo_id=None, situacion_id=None):
    if individuo_id:
        individuo = Individuo.objects.get(pk=individuo_id)
        #Generamos nueva situacion a partir de la anterio
        situacion = individuo.get_situacion()
    elif situacion_id:
        situacion = Situacion.objects.get(pk=situacion_id)
        individuo = situacion.individuo
    #Le actualizamos la fecha
    situacion.fecha = timezone.now()
    form = SituacionForm(instance=situacion)
    #Trabajamos
    if request.method == "POST":
        form = SituacionForm(request.POST, instance=situacion)
        if form.is_valid():
            situacion = form.save(commit=False)
            situacion.individuo = individuo
            situacion.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Situacion", 'form': form, 'boton': "Cargar", }) 

@permission_required('operadores.individuos')
def del_situacion(request, situacion_id=None):
    #Obtenemos los datos
    situacion = Situacion.objects.get(pk=situacion_id)
    individuo = situacion.individuo
    #Si es actual, cambiamos
    if situacion == individuo.situacion_actual:
        individuo.situacion_actual = individuo.situaciones.exclude(pk=situacion.pk).last()
        individuo.save()
    #Eliminamos
    situacion.delete()
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Signos Vitales
@permission_required('operadores.individuos')
def cargar_signosvitales(request, individuo_id, signosvitales_id=None):
    signosvitales = None
    if signosvitales_id:
        signosvitales = SignosVitales.objects.get(pk=signosvitales_id)
    form = SignosVitalesForm(instance=signosvitales)
    if request.method == "POST":
        form = SignosVitalesForm(request.POST, instance=signosvitales)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            signosvitales = form.save(commit=False)
            signosvitales.individuo = individuo
            form.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Signos Vitales", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def del_signosvitales(request, signosvitales_id):
    signosvitales = SignosVitales.objects.get(pk=signosvitales_id)
    individuo = signosvitales.individuo
    signosvitales.delete()
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Relacion
@permission_required('operadores.individuos')
def cargar_relacion(request, individuo_id, relacion_id=None):
    relacion = None
    if relacion_id:
        relacion = Relacion.objects.get(pk=relacion_id)
    individuo = Individuo.objects.get(pk=individuo_id)
    form = RelacionForm(instance=relacion, initial={'individuo': individuo, })
    if request.method == "POST":
        form = RelacionForm(request.POST, instance=relacion)
        if form.is_valid():
            relacion = form.save(commit=False)
            relacion.individuo = individuo
            form.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Relacion", 'form': form, 'boton': "Cargar", }) 

@permission_required('operadores.individuos')
def del_relacion(request, relacion_id):
    relacion = Relacion.objects.get(pk=relacion_id)
    individuo = relacion.individuo
    relacion.delete()
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Atributos
@permission_required('operadores.individuos')
def cargar_atributo(request, individuo_id, atributo_id=None, tipo=None):
    atributo = Atributo(tipo=tipo)
    if atributo_id:
        atributo = Atributo.objects.get(pk=atributo_id)
    form = AtributoForm(instance=atributo)
    if request.method == "POST":
        form = AtributoForm(request.POST, instance=atributo)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            atributo = form.save(commit=False)
            atributo.individuo = individuo
            atributo.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Atributo", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def del_atributo(request, atributo_id):
    atributo = Atributo.objects.get(pk=atributo_id)
    individuo = atributo.individuo
    atributo.delete()
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Sintomas
@permission_required('operadores.individuos')
def cargar_sintoma(request, individuo_id, sintoma_id=None):
    sintoma = None
    if sintoma_id:
        sintoma = Sintoma.objects.get(pk=sintoma_id)
    form = SintomaForm(instance=sintoma)
    if request.method == "POST":
        form = SintomaForm(request.POST, instance=sintoma)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            sintoma = form.save(commit=False)
            sintoma.individuo = individuo
            sintoma.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Sintoma", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def del_sintoma(request, sintoma_id):
    sintoma = Sintoma.objects.get(pk=sintoma_id)
    individuo = sintoma.individuo
    sintoma.delete()
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Patologia
@permission_required('operadores.individuos')
def cargar_patologia(request, individuo_id, patologia_id=None):
    patologia = None
    if patologia_id:
        patologia = Patologia.objects.get(pk=patologia_id)
    form = PatologiaForm(instance=patologia)
    if request.method == "POST":
        form = PatologiaForm(request.POST, instance=patologia)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            patologia = form.save(commit=False)
            patologia.individuo = individuo
            patologia.save()
            return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Patologia", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def del_patologia(request, patologia_id):
    patologia = Patologia.objects.get(pk=patologia_id)
    individuo = patologia.individuo
    patologia.delete()
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#Documento
def cargar_documento(request, individuo_id, documento_id=None, tipo=None):
    documento = None
    #Depende el caso
    if documento_id:
        documento = Documento.objects.get(pk=documento_id)
        form = FileForm(initial={'archivo': documento.archivo})
    elif tipo:
        form = FileForm()
    else:
        form = DocumentoForm(initial={'tipo': tipo},instance=documento)
    #Procesamos carga
    if request.method == "POST":
        individuo = Individuo.objects.get(pk=individuo_id)
        if documento_id or tipo:
            form = FileForm(request.POST, request.FILES)
            if form.is_valid():
                if documento:#Solo si tenemos que modificar
                    documento.archivo = form.cleaned_data['archivo']
                else:#Si creamos uno nuevo de un tipo especifico
                    documento = Documento(individuo=individuo)
                    documento.tipo = tipo
                    documento.archivo = form.cleaned_data['archivo']
                    documento.aclaracion = "minimalista"
                documento.save()
                return render(request, "extras/close.html")
        else:#Si es un docu nuevo:
            form = DocumentoForm(request.POST, request.FILES)
            if form.is_valid():
                documento = form.save(commit=False)
                documento.individuo = individuo
                documento.save()
                return render(request, "extras/close.html")
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Documento", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def del_documento(request, documento_id):
    documento = Documento.objects.get(pk=documento_id)
    individuo = documento.individuo
    documento.delete()
    return redirect('informacion:ver_individuo', individuo_id=individuo.id)

#GEOPOS
@permission_required('operadores.individuos')
def cargar_geoposicion(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    if request.method == "POST":
        geoposicion = GeoPosicion()
        geoposicion.individuo = individuo
        geoposicion.latitud = request.POST['latitud']
        geoposicion.longitud = request.POST['longitud']
        if request.POST['observaciones'] != '':
            geoposicion.aclaracion = request.POST['observaciones']
        else:
            geoposicion.aclaracion = "Carga Manual de " + str(obtener_operador(request))
        geoposicion.save()
        return render(request, "extras/close.html")
    return render(request, "extras/gmap_form.html", {
        'objetivo': individuo, 
        'gkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
    })

#Reportes en el sistema
@permission_required('operadores.reportes')
def tablero_control(request):
    #Ubicaciones Estrategicas
    ubicaciones = Ubicacion.objects.select_related('localidad')
    aislamientos = ubicaciones.filter(tipo='AI')
    internaciones = ubicaciones.filter(tipo='IN')
    #Conteo por Nacionalidades
    nacionalidades = Nacionalidad.objects.annotate(cantidad=Count('individuos'))
    nacionalidades = nacionalidades.exclude(cantidad=0)
    nacionalidades = nacionalidades.order_by('-cantidad')
    nacionalidades = nacionalidades[:10]
    #Conteo de estados
    estados = []
    for estado in TIPO_ESTADO:
        cant = Individuo.objects.filter(situacion_actual__estado=estado[0]).count()
        if cant > 0:
            #Obtenemos cant ultimas 24 horas
            last_24 = Individuo.objects.filter(
                situacion_actual__estado=estado[0],
                situacion_actual__fecha__gt=timezone.now()-timedelta(hours=24)
                ).count()
            #Agregamos registro
            estados.append([estado[0], estado[1], cant, last_24])
    #Conteo Conductas
    conductas = []
    for conducta in TIPO_CONDUCTA:
        cant = Individuo.objects.filter(situacion_actual__conducta=conducta[0]).count()
        if cant > 0:
            #Obtenemos cant ultimas 24 horas
            last_24 = Individuo.objects.filter(
                situacion_actual__conducta=conducta[0],
                situacion_actual__fecha__gt=timezone.now()-timedelta(hours=24)
                ).count()
            #Agregamos registro
            conductas.append([conducta[0], conducta[1], cant, last_24])
    #GRAFICACION
    #Fechas del Grafico
    dias = [timezone.now() - timedelta(days=x) for x in range(0,15)]
    dias = [dia.date() for dia in dias]
    dias.reverse()
    #Obtenemos o Generamos Grafico de Estados:
    #Traemos inviduos con optimizacion de campos
    individuos = Individuo.objects.exclude(situacion_actual=None)
    individuos = individuos.select_related('situacion_actual')
    #Procesamos info
    graf_estados = obtener_grafico('graf_estados', 'Grafico Acumulativo de Estados', 'L')
    for dia in dias:
        if not graf_estados.update or ( graf_estados.update < dia ):
            for estado in TIPO_ESTADO:
                cant = individuos.filter(
                    situacion_actual__estado=estado[0],
                    situacion_actual__fecha__date__lte=dia).count()
                graf_estados.agregar_dato(dia, estado[1], date2str(dia), cant)
    #Obtenemos o generamos grafico de Conductas
    graf_conductas = obtener_grafico('graf_conductas', 'Grafico Acumulativo de Conductas', 'L')
    for dia in dias:
        if not graf_conductas.update or ( graf_conductas.update < dia ):
            for conducta in TIPO_CONDUCTA:
                cant = individuos.filter(
                    situacion_actual__conducta=conducta[0],
                    situacion_actual__fecha__date__lte=dia).count()
                graf_conductas.agregar_dato(dia, conducta[1], date2str(dia), cant)
    #Entregamos el reporte
    return render(request, "reportes/tablero_control.html", {
        'aislamientos': aislamientos,
        'internaciones': internaciones,
        "nacionalidades": nacionalidades,
        "estados": estados,
        "graf_estados": graf_estados,
        "conductas": conductas,
        "graf_conductas": graf_conductas,
    })

#IMPORTANTE: CORREGIR QUE SOLO IMPORTE EL ULTIMO ESTADO
@permission_required('operadores.reportes')
def reporte_basico(request):
    #Definimos un objecto para jugar
    class Creportado(object):
        individuo = Individuo()
        atributos = 0
        sintomas = 0
    #iniciamos la vista
    estados = TIPO_ESTADO
    conductas = TIPO_CONDUCTA
    atributos = TIPO_ATRIBUTO
    sintomas = TIPO_SINTOMA
    if request.method == "POST":
        reportados = {}
        #Obtenemos todos los parametros
        #begda = request.POST['begda']
        #endda = request.POST['endda']
        estados = request.POST.getlist('estado')
        conductas = request.POST.getlist('conducta')
        #Individuos
        full_individuos = Individuo.objects.all()
        #Obtenemos todos los individuos que esten en situacion especificada
        full_individuos = full_individuos.filter(situacion_actual__estado__in=estados)
        full_individuos = full_individuos.filter(situacion_actual__conducta__in=conductas)        
        #Descartamos por Atributos
        atributos = request.POST.getlist('atributo')
        full_individuos = full_individuos.filter(atributos__tipo__in=atributos)
        #Descartamos por Sintomas
        sintomas = request.POST.getlist('sintoma')
        full_individuos = full_individuos.filter(sintomas__tipo__in=sintomas)
        #Obtenemos cantidad de sintomas y de atributos:
            #Aca deberiamos ordenar por sintomas y atributos
        #Optimizamos
        full_individuos = full_individuos.prefetch_related('domicilios', 'situaciones', 'atributos', 'sintomas')
        return render(request, "reportes/reporte_basico_mostrar.html", {
            'reportados': full_individuos,
            'has_table': True,
        })
    return render(request, "reportes/reporte_basico_buscar.html", {
        'estados': estados,
        'conductas': conductas,
        'atributos': atributos, 
        'sintomas': sintomas,
    })

@permission_required('operadores.menu_georef')
def lista_ingresos_hoteles(request):
    form = ReporteHotelesForm()
    if request.method == "POST":
        form = ReporteHotelesForm(request.POST)
        if form.is_valid():
            begda = form.cleaned_data['begda']
            endda = form.cleaned_data['endda']
            #Filtramos esos domicilios
            domicilios = Domicilio.objects.exclude(ubicacion=None)
            domicilios = domicilios.filter(fecha__date__range=(begda, endda))
            #Con esos domicilios buscamos los individuos
            individuos = Individuo.objects.filter(domicilios__in=domicilios)
            #Eliminamos repetidos
            individuos = individuos.distinct()
            #Optimizamos
            individuos = individuos.select_related('nacionalidad')
            individuos = individuos.select_related('domicilio_actual', 'domicilio_actual__ubicacion', 'domicilio_actual__localidad')
            individuos = individuos.select_related('situacion_actual')
            individuos = individuos.prefetch_related('domicilios', 'domicilios__ubicacion', 'domicilios__localidad')
            #Ordenamos
            individuos = individuos.order_by('domicilio_actual__fecha')
            return render(request, "ingresos_hoteles.html", {
                'individuos': individuos,
                'begda': begda, 'endda': endda,
                'has_table': True,
            })
    return render(request, "extras/generic_form.html", {'titulo': "Reporte de Ingreso a Hoteles", 'form': form, 'boton': "Buscar", })