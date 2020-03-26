#Imports Django
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from coe.settings import GEOPOSITION_GOOGLE_MAPS_API_KEY
from core.decoradores import superuser_required
from core.forms import SearchForm
from operadores.functions import obtener_operador
from background.tasks import crear_progress_link
#imports de la app
from .choices import TIPO_ESTADO, TIPO_CONDUCTA
from .models import Archivo
from .models import Vehiculo, ControlVehiculo, Origen
from .models import Individuo
from .models import Seguimiento
from .models import Domicilio, GeoPosicion
from .models import Atributo, Sintoma
from .models import TipoAtributo, TipoSintoma
from .forms import ArchivoForm, ArchivoFormWithPass
from .forms import VehiculoForm, ControlVehiculoForm
from .forms import IndividuoForm, BuscadorIndividuosForm
from .forms import DomicilioForm, AtributoForm, SintomaForm
from .forms import SituacionForm, RelacionForm, SeguimientoForm
from .forms import SearchIndividuoForm, SearchVehiculoForm
from .forms import PermisoForm
from .tasks import guardar_same, guardar_epidemiologia
from .tasks import guardar_padron_individuos, guardar_padron_domicilios

#Publico
def pedir_permiso(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = PermisoForm(
        initial={
            'individuo':individuo, 
        })
    return render(request, "pedir_permiso.html", {'form': form, 'individuo': individuo, })

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
    return render(request, 'archivos_pendientes.html', {'archivos': archivos,})

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
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Subir Archivo para Carga", 'form': form, 'boton': "Subir", })

@permission_required('operadores.archivos')
def subir_same(request):
    form = ArchivoForm(initial={'tipo':5, 'nombre': str(timezone.now())[0:16]})
    if request.method == "POST":
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            lines = lines[1:]
            tarea = crear_progress_link("SUBIR_SAME:"+str(timezone.now()))
            frag_size = 25#Dividimos en fragmentos de 25
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:
                guardar_same(segmento, archivo_id=archivo.id, queue=tarea)
            guardar_same(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "CARGA MASIVA SAME", 'form': form, 'boton': "Subir", })

@permission_required('operadores.archivos')
def procesar_archivos(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id)
    archivo.procesado = not archivo.procesado
    archivo.save()
    return redirect('informacion:ver_archivo', archivo_id=archivo.id)

#VEHICULOS
@permission_required('operadores.ver_individuo')
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
    #Cargamos Form Inicial
    form = VehiculoForm(
        instance=vehiculo,
        initial={'identificacion': identificacion, }
    )
    if request.method == "POST":
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            operador = obtener_operador(request)
            vehiculo = form.save(commit=False)
            vehiculo.operador = operador
            vehiculo.save()
            return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Vehiculo", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.vehiculos')
def cargar_control(request, vehiculo_id):
    vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
    form = ControlVehiculoForm()
    if request.method == "POST":
        form = ControlVehiculoForm(request.POST)
        if form.is_valid():
            control = form.save(commit=False)
            control.vehiculo = vehiculo
            form.save()
            return redirect('informacion:ver_vehiculo', vehiculo_id=vehiculo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Control Vehicular", 'form': form, 'boton': "Cargar", }) 

#INDIVIDUOS
@permission_required('operadores.individuos')
def buscar_individuo(request, control_id=None):
    form = SearchIndividuoForm()
    if request.method == "POST":
        form = SearchIndividuoForm(request.POST)
        if form.is_valid():
            num_doc = form.cleaned_data['num_doc']
            num_doc = num_doc.upper()
            try:
                individuo = Individuo.objects.get(num_doc=num_doc)
                if control_id:#lo cargamos en el vehiculo y volvemos al vehiculo:
                    control = ControlVehiculo.objects.get(pk=control_id)
                    origen = Origen(control=control, individuo=individuo)
                    origen.save()
                    return redirect('informacion:ver_vehiculo', vehiculo_id=control.vehiculo.id)
                else:#Se va a la planilla simplemente
                    return redirect('informacion:ver_individuo', individuo_id=individuo.id)
            except Individuo.DoesNotExist:
                if control_id:#Se carga en un vehiculo:
                    return redirect('informacion:cargar_pasajero_nuevo', num_doc=num_doc, control_id=control_id)
                else:
                    return redirect('informacion:cargar_individuo', num_doc=num_doc)
    return render(request, "extras/generic_form.html", {'titulo': "Indicar Documento de Individuo", 'form': form, 'boton': "Buscar", })

@permission_required('operadores.individuos')
def cargar_individuo(request, control_id=None, individuo_id=None, num_doc=None):
    individuo = None
    if individuo_id:#Si manda individuo es para modificar
        individuo = Individuo.objects.get(pk=individuo_id)
        domicilio_actual = individuo.domicilio_actual()
        if domicilio_actual:
            form = IndividuoForm(
                instance=individuo,
                initial={
                    'dom_localidad': individuo.localidad_actual,
                    'dom_calle': domicilio_actual.calle,
                    'dom_numero': domicilio_actual.numero,
                    'dom_aclaracion': domicilio_actual.aclaracion,
                    'atributos': [a.tipo.id for a in individuo.atributos.all()],
                    'sintomas': [s.tipo.id for s in individuo.sintomas.all()],
                }
            )
        else:
            form = IndividuoForm(
                instance=individuo,
                initial={
                    'atributos': [a.tipo.id for a in individuo.atributos.all()],
                    'sintomas': [s.tipo.id for s in individuo.sintomas.all()],
                }
            )
    else:
        form = IndividuoForm(initial={"num_doc":num_doc})
    #Analizamos si mando informacion:
    if request.method == "POST":
        form = IndividuoForm(request.POST, instance=individuo)
        if form.is_valid():
            operador = obtener_operador(request)
            individuo = form.save(commit=False)
            individuo.operador = operador
            individuo.save()
            #Generamos modelos externos:
            #Creamos domicilio
            domicilio = Domicilio()
            domicilio.individuo = individuo
            if form.cleaned_data['dom_localidad']:
                domicilio.localidad = form.cleaned_data['dom_localidad']
                domicilio.calle = form.cleaned_data['dom_calle']
                domicilio.numero = form.cleaned_data['dom_numero']
                domicilio.aclaracion = form.cleaned_data['dom_aclaracion']
                domicilio.save()
            #Creamos atributos
            atributos = form.cleaned_data['atributos']
            individuo.atributos.all().delete()
            for atributo_id in atributos:
                atributo = Atributo()
                atributo.individuo = individuo
                atributo.tipo = TipoAtributo.objects.get(pk=atributo_id)
                atributo.save()           
            #Creamos sintomas
            sintomas = form.cleaned_data['sintomas']
            individuo.sintomas.all().delete()
            for sintoma_id in sintomas:
                sintoma = Sintoma()
                sintoma.individuo = individuo
                sintoma.tipo = TipoSintoma.objects.get(pk=sintoma_id)
                sintoma.save()  
            #Si vino en un vehiculo
            if control_id:
                control = ControlVehiculo.objects.get(pk=control_id)
                origen = Origen(control=control, individuo=individuo)
                origen.save()
                return redirect('informacion:ver_vehiculo', vehiculo_id=control.vehiculo.id)
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "cargar_individuo.html", {'titulo': "Cargar Individuo", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def ver_individuo(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    return render(request, "ver_individuo.html", {'individuo': individuo, })

#LISTAS
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
                individuos = individuos.filter(domicilios__calle=form.cleaned_data['calle'])
            if form.cleaned_data['localidad']:
                individuos = individuos.filter(domicilios__localidad=form.cleaned_data['localidad'])
            #Optimizamos las busquedas a la db
            individuos = individuos.select_related('nacionalidad', 'origen', 'destino', )
            individuos = individuos.prefetch_related('atributos', 'sintomas', 'situaciones', 'relaciones')
            individuos = individuos.prefetch_related('atributos__tipo', 'sintomas__tipo')
            #Eliminamos repetidos
            individuos = individuos.distinct()
            #Mandamos el listado
            return render(request, "lista_individuos.html", {
                'individuos': individuos,
                'has_table': True,
            })
    return render(request, "extras/generic_form.html", {'titulo': "Buscador de Individuos", 'form': form, 'boton': "Buscar", })

@permission_required('operadores.individuos')
def lista_evaluar(request):
    evaluar = []
    individuos = Individuo.objects.filter(situaciones__conducta='B')
    individuos = individuos.select_related('nacionalidad', 'origen', 'destino', )
    individuos = individuos.prefetch_related('atributos', 'sintomas', 'situaciones', 'relaciones')
    individuos = individuos.prefetch_related('atributos__tipo', 'sintomas__tipo')
    for individuo in individuos:
        if individuo.situacion_actual().conducta == 'B':
            evaluar.append(individuo)
    return render(request, "lista_individuos.html", {
        'individuos': evaluar,
        'has_table': True,
    })

@permission_required('operadores.individuos')
def lista_seguimiento(request):
    individuos = {}
    seguimientos = Seguimiento.objects.all().exclude(tipo='F')#Eliminamos los que terminaron el seguimiento
    seguimientos = seguimientos.select_related('individuo', 'individuo__nacionalidad')
    seguimientos = seguimientos.prefetch_related('individuo__atributos', 'individuo__sintomas')
    seguimientos = seguimientos.prefetch_related('individuo__situaciones', 'individuo__seguimientos')
    seguimientos = seguimientos.prefetch_related('individuo__atributos__tipo', 'individuo__sintomas__tipo')
    seguimientos = [s for s in seguimientos]
    seguimientos_terminados = [s.individuo for s in Seguimiento.objects.filter(tipo='F')]
    for seguimiento in seguimientos:
        if seguimiento.individuo.id not in individuos:
            if not seguimiento.individuo in seguimientos_terminados:
                individuos[seguimiento.individuo.id] = seguimiento.individuo
    individuos = list(individuos.values())
    return render(request, "listado_seguimiento.html", {
        'individuos': individuos,
        'has_table': True,
    })

#CARGA DE ELEMENTOS
@permission_required('operadores.individuos')
def cargar_domicilio(request, individuo_id):
    form = DomicilioForm()
    if request.method == "POST":
        form = DomicilioForm(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            domicilio = form.save(commit=False)
            domicilio.individuo = individuo
            domicilio.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Domicilio", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def cargar_situacion(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = SituacionForm(initial={'individuo': individuo, })
    if request.method == "POST":
        form = SituacionForm(request.POST)
        if form.is_valid():
            situacion = form.save(commit=False)
            situacion.individuo = individuo
            situacion.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Situacion", 'form': form, 'boton': "Cargar", }) 

@permission_required('operadores.individuos')
def cargar_seguimiento(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = SeguimientoForm(initial={'individuo': individuo, })
    if request.method == "POST":
        form = SeguimientoForm(request.POST)
        if form.is_valid():
            seguimiento = form.save(commit=False)
            seguimiento.individuo = individuo
            form.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Seguimiento", 'form': form, 'boton': "Cargar", }) 

@permission_required('operadores.individuos')
def cargar_relacion(request, individuo_id):
    individuo = Individuo.objects.get(pk=individuo_id)
    form = RelacionForm(initial={'individuo': individuo, })
    if request.method == "POST":
        form = RelacionForm(request.POST)
        if form.is_valid():
            relacion = form.save(commit=False)
            relacion.individuo = individuo
            form.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Relacion", 'form': form, 'boton': "Cargar", }) 

@permission_required('operadores.individuos')
def cargar_atributo(request, individuo_id):
    form = AtributoForm()
    if request.method == "POST":
        form = AtributoForm(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            sintoma = form.save(commit=False)
            sintoma.individuo = individuo
            sintoma.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Atributo", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def cargar_sintoma(request, individuo_id):
    form = SintomaForm()
    if request.method == "POST":
        form = SintomaForm(request.POST)
        if form.is_valid():
            individuo = Individuo.objects.get(pk=individuo_id)
            sintoma = form.save(commit=False)
            sintoma.individuo = individuo
            sintoma.save()
            return redirect('informacion:ver_individuo', individuo_id=individuo.id)
    return render(request, "extras/generic_form.html", {'titulo': "Cargar Sintoma", 'form': form, 'boton': "Cargar", })

@permission_required('operadores.individuos')
def cargar_geoposicion(request, domicilio_id):
    domicilio = Domicilio.objects.get(pk=domicilio_id)
    if request.method == "POST":
        if hasattr(domicilio,'geoposicion'):
            geoposicion = domicilio.geoposicion
        else:
            geoposicion = GeoPosicion()
            geoposicion.domicilio = domicilio
        #cargamos los datos del form:
        geoposicion.latitud = request.POST['latitud']
        geoposicion.longitud = request.POST['longitud']
        geoposicion.observaciones = request.POST['observaciones']
        geoposicion.save()
        return redirect('informacion:ver_individuo', individuo_id=domicilio.individuo.id)
    return render(request, "extras/gmap_form.html", {
        'objetivo': domicilio.individuo, 
        'gkey': GEOPOSITION_GOOGLE_MAPS_API_KEY,
    })

#Reportes en el sistema
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
    atributos = TipoAtributo.objects.all()
    sintomas = TipoSintoma.objects.all()
    if request.method == "POST":
        reportados = {}
        #Obtenemos todos los parametros
        #begda = request.POST['begda']
        #endda = request.POST['endda']
        estados = request.POST.getlist('estado')
        conductas = request.POST.getlist('conducta')
        atributos = request.POST.getlist('atributo')
        sintomas = request.POST.getlist('sintoma')
        #Obtenemos todos los individuos que esten en ese estado
        full_individuos = Individuo.objects.filter(
            situaciones__estado__in=estados,
            situaciones__conducta__in=conductas).distinct()
        for atributo in atributos:
            individuos = full_individuos.filter(atributos__tipo=atributo)
            for individuo in individuos:
                if individuo.id not in reportados:#Si no esta lo agregamos
                    reportado = Creportado()
                    reportado.individuo = individuo
                    reportados[reportado.individuo.id] = reportado
                #Le sumamos 1 a ese atributo
                reportados[individuo.id].atributos += 1
        for sintoma in sintomas:
            individuos = full_individuos.filter(sintomas__tipo=sintoma)
            for individuo in individuos:
                if individuo.id not in reportados:#Si no esta lo agregamos
                    reportado = Creportado()
                    reportado.individuo = individuo
                    reportados[reportado.individuo.id] = reportado
                #Le sumamos 1 a ese atributo
                reportados[individuo.id].sintomas += 1
        #los volvemos una lista:
        reportados = list(reportados.values())
        reportados.sort(key=lambda x: x.sintomas, reverse=True)
        return render(request, "reporte_basico_mostrar.html", {'reportados': reportados, })
    return render(request, "reporte_basico_buscar.html", {
        'estados': estados, 'conductas': conductas,
        'atributos': atributos, 'sintomas': sintomas, })

@permission_required('operadores.reportes')
def csv_individuos(request):
    individuos = Individuo.objects.all()
    individuos = individuos.prefetch_related('atributos', 'sintomas')
    #Iniciamos la creacion del csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="individuos.csv"'
    writer = csv.writer(response)
    writer.writerow(['REPORTE DE INDIVIDUOS'])
    writer.writerow(['TIPO DOC', 'NUM DOC', 'APELLIDO', 'NOMBRE', 'NACIONALIDAD', 'ORIGEN', 'DESTINO LOCAL', 'OBSERVACIONES', 'ATRIBUTOS','SINTOMAS'])
    for individuo in individuos:
        writer.writerow([
            individuo.get_tipo_doc_display(),
            individuo.num_doc,
            individuo.apellidos,
            individuo.nombres,
            individuo.nacionalidad.nombre,
            str(individuo.origen),
            str(individuo.destino),
            individuo.observaciones,
            str([a.tipo.nombre for a in individuo.atributos.all()]),
            str([s.tipo.nombre for s in individuo.sintomas.all()]),
        ])
    #Enviamos el archivo para descargar
    return response

#CARGAS MASIVAS
@superuser_required
def upload_padron_individuos(request):
    form = ArchivoFormWithPass()
    if request.method == "POST":
        form = ArchivoFormWithPass(request.POST, request.FILES)
        if form.is_valid():
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            tarea = crear_progress_link("SUBIR_PADRON:"+str(timezone.now()))
            #Dividimos en fragmentos
            frag_size = 10000
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:#Procesamos todos menos el ultimo
                guardar_padron_individuos(segmento, archivo_id=archivo.id, queue=tarea)
            #Para que marque el archivo como terminado
            guardar_padron_individuos(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "CARGA MASIVA PADRON INDIVIDUOS", 'form': form, 'boton': "Subir", })

@superuser_required
def upload_padron_domicilios(request):
    form = ArchivoFormWithPass()
    if request.method == "POST":
        form = ArchivoFormWithPass(request.POST, request.FILES)
        if form.is_valid():
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            tarea = crear_progress_link("SUBIR_PADRON:"+str(timezone.now()))
            #Dividimos en fragmentos
            frag_size = 10000
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:#Procesamos todos menos el ultimo
                guardar_padron_domicilios(segmento, archivo_id=archivo.id, queue=tarea)
            #Para que marque el archivo como terminado
            guardar_padron_domicilios(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "CARGA MASIVA PADRON DOMICILIOS", 'form': form, 'boton': "Subir", })

@superuser_required
def subir_epidemiologia(request):
    form = ArchivoFormWithPass(initial={'tipo':6, 'nombre': str(timezone.now())[0:16]})
    if request.method == "POST":
        form = ArchivoFormWithPass(request.POST, request.FILES)
        if form.is_valid():
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            lines = lines[1:]
            tarea = crear_progress_link("SUBIR_EPIDEMIOLOGIA:"+str(timezone.now()))
            frag_size = 100#Dividimos en fragmentos de 100
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:
                guardar_epidemiologia(segmento, archivo_id=archivo.id, queue=tarea)
            guardar_epidemiologia(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "CARGA MASIVA EPIDEMIOLOGIA", 'form': form, 'boton': "Subir", })