#Imports de Python
import io
import logging
import traceback
from datetime import timedelta
#Imports de django
from django.db.models import Q, Count
from django.utils import timezone
from django.core.files import File
from django.core.cache import cache
#Imports Extras:
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
#Imports del Proyeto
from coe.settings import STATIC_ROOT, MEDIA_ROOT
from coe.constantes import DIAS_CUARENTENA, NOTEL
from informacion.models import Individuo, Situacion, Atributo, Documento
from app.functions import desactivar_tracking
#Imports de la app
from .choices import TIPO_VIGIA
from .models import Seguimiento
from .models import Vigia
from .models import OperativoVehicular

#Logger
logger = logging.getLogger('functions')

#Definimos funciones
def obtener_bajo_seguimiento():
    #Obtenemos los en cuarentena obligatorio o aislamiento
    individuos = Individuo.objects.filter(situacion_actual__conducta__in=('D', 'E'))
    #Devolvemos listado
    return individuos

def esperando_seguimiento(individuos=None):
    #Si ya paso el tiempo definido para aislamiento no tiene sentido seguirlos
    limite = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Comenzamos a filtrar
    if not individuos:
        tipos = [t[0] for t in TIPO_VIGIA]
        vigilancia_actual = Atributo.objects.filter(tipo__in=tipos, fecha__gt=limite)
        individuos = Individuo.objects.filter(atributos__in=vigilancia_actual)
    #descartamos los que recibieron alta en la ultima semana:
    altas_nuevas = Seguimiento.objects.filter(fecha__gt=limite, tipo="FS")
    individuos = individuos.exclude(seguimientos__in=altas_nuevas)
    #descartamos los que no tienen telefono
    individuos = individuos.exclude(seguimientos__tipo="TE")
    #evitamos repetidos
    individuos = individuos.distinct()
    #devolvemos listado
    return individuos

def vigilancias_faltantes(individuos):#Debe ser queryset
    #Optimizamos busqueda necesaria
    individuos = individuos.prefetch_related("atributos", "vigiladores")
    #Generamos listado de las vigilancias que requiere:
    tipos_vigilancia = [t[0] for t in TIPO_VIGIA]
    limite = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    for individuo in individuos:
        individuo.requiere = []
        vigilancias_tiene = [vigia.tipo for vigia in individuo.vigiladores.all()]
        vigilancia_faltantes = [tipo for tipo in tipos_vigilancia if tipo not in vigilancias_tiene]
        for atrib in individuo.atributos.all():
            if atrib.tipo in vigilancia_faltantes and atrib.fecha > limite:
                individuo.requiere.append(atrib)
    return individuos

def asignar_vigilante(individuo, tipo):
    #Iniciamos proceso de asignacion:
    try:
        #Chequeamos que tenga telefono:
        if individuo.telefono not in (NOTEL, ""):
            #Buscamos vigilante
            if not individuo.vigiladores.filter(tipo=tipo).exists():#Si no tiene ese tipo de Vigilante
                #Si es Vigilancia Medica, lo sacamos de Epidemiologia:
                if tipo == "ST":#(ODIO HARDCODEAR)
                    for vigia in individuo.vigiladores.filter(tipo="VE"):
                        vigia.del_vigilado(individuo)
                #Intentamos buscar vigilante asignado a algun relacionado:
                for relacion in individuo.relaciones.exclude(relacionado__vigiladores=None):
                    try:
                        vigia = relacion.relacionado.vigiladores.get(tipo=tipo)
                        vigia.add_vigilado(individuo)
                        break#Lo cargamos, limpiamos, terminamos
                    except:
                        pass#No tenia de ese tipo
                if not individuo.vigiladores.filter(tipo=tipo).exists():#Si no tiene Vigilante
                    #Intentamos buscarle el vigilante que menos asignados tenga
                    vigias = Vigia.objects.filter(tipo=tipo).annotate(cantidad=Count('controlados')).exclude(activo=False)
                    for vigia in vigias.order_by('-priorizar', 'cantidad'):
                        if vigia.max_controlados > vigia.cantidad:
                            vigia.add_vigilado(individuo)
                            break#Lo cargamos, limpiamos, terminamos
        else:
            #No tiene telefono
            if not individuo.seguimientos.filter(tipo="TE").exists():
                #Si no esta informada la falta, le metemos seguimiento: "TE"
                seg = Seguimiento(individuo=individuo)
                seg.tipo = "TE"
                seg.aclaracion = "Se intento asignar Vigilante, no tiene telefono"
                seg.save()
    except:
        logger.info("Fallo asignar_vigilante: :\n"+str(traceback.format_exc()))

def crear_doc_descartado(seguimiento):
    try:
        #Generamos informacion base
        individuo = seguimiento.individuo
        fecha = seguimiento.fecha.date()
        #Se crea un pdf utilizando reportLab
        packet = io.BytesIO()
        pdf = canvas.Canvas(packet, pagesize = A4)
        pdf.setFont('Times-Roman', 13)
        pdf.drawString(85, 635, individuo.apellidos + ', ' + individuo.nombres + ' - ' + individuo.get_tipo_doc_display() + ': ' + str(individuo.num_doc))
        pdf.setFont('Times-Roman', 16)
        pdf.drawString(250, 115, str(fecha))
        pdf.save()
        # Nos movemos al comienzo del búfer StringIO
        packet.seek(0)
        nuevo_pdf = PdfFileReader(packet)
        # Leemos el pdf base
        existe_pdf = PdfFileReader(STATIC_ROOT+'/archivo/test_negativo.pdf', "rb")
        salida = PdfFileWriter()
        # Se agregan los datos de la persona que será dada de alta, al pdf ya existente
        pagina = existe_pdf.getPage(0)
        pagina.mergePage(nuevo_pdf.getPage(0))
        salida.addPage(pagina)
        # Finalmente se escribe la salida, en un archivo real
        path = MEDIA_ROOT+'/informacion/descartado/'+individuo.num_doc+'_'+str(fecha)+".pdf"
        outputStream = open(path, "wb")
        salida.write(outputStream)
        outputStream.close()
        #Devolvemos el archivo para guardar:
        return '/informacion/descartado/'+individuo.num_doc+'_'+str(fecha)+".pdf"
    except:
        logger.info("No se creo PDF para: " + str(individuo))
        logger.info("Motivo: " + str(traceback.format_exc()))

def creamos_doc_aislamiento(seguimiento):
    try:
        #Obtenemos informacion inicial
        individuo = seguimiento.individuo
        operador = seguimiento.operador
        individuo_txt = individuo.apellidos + ', ' + individuo.nombres + ' (' + individuo.get_tipo_doc_display() + ': ' + str(individuo.num_doc) + ')'
        inicio = seguimiento.fecha.date()
        #Se crea un pdf utilizando reportLab
        packet = io.BytesIO()
        pdf = canvas.Canvas(packet, pagesize = A4)
        pdf.setFont('Times-Roman', 12)
        #comenzamos a escribir la informacion
        pdf.drawString(200, 630, individuo_txt)
        pdf.drawString(150, 580, str(inicio))
        pdf.drawString(350, 215, "Operador del COE:")
        pdf.drawString(350, 200, operador.apellidos + ', ' + operador.nombres)
        pdf.drawString(350, 180, operador.num_doc)
        pdf.save()
        # Nos movemos al comienzo del búfer StringIO
        packet.seek(0)
        nuevo_pdf = PdfFileReader(packet)
        # Leemos el pdf base
        pdf_base = PdfFileReader(STATIC_ROOT+'/archivo/certificado_aislamiento.pdf', "rb")
        # Se agregan los datos de la persona que será dada de alta, al pdf ya existente
        salida = PdfFileWriter()
        pagina = pdf_base.getPage(0)
        pagina.mergePage(nuevo_pdf.getPage(0))
        salida.addPage(pagina)
        # Finalmente se escribe la salida, en un archivo real
        path = MEDIA_ROOT+'/informacion/aislamiento/'+individuo.num_doc+'_'+str(inicio)+".pdf"
        outputStream = open(path, "wb")
        salida.write(outputStream)
        outputStream.close()
        #Devolvemos el archivo para guardar:
        return '/informacion/aislamiento/'+individuo.num_doc+'_'+str(inicio)+".pdf"
    except:
        logger.info("No se creo PDF para: " + str(individuo))
        logger.info("Motivo: " + str(traceback.format_exc()))    

def creamos_doc_alta_seguimiento(individuo):
    try:
        packet = io.BytesIO()
        #Se crea un pdf utilizando reportLab
        pdf = canvas.Canvas(packet, pagesize = A4)
        pdf.setFont('Times-Roman', 12)
        pdf.drawString(110, 560, individuo.apellidos + ', ' + individuo.nombres + ' - ' + individuo.get_tipo_doc_display() + ': ' + str(individuo.num_doc))
        inicio = individuo.situaciones.filter(conducta__in=('D','E')).last().fecha
        fin = inicio + timedelta(days=DIAS_CUARENTENA)
        pdf.drawString(110, 545, "Inicio Su Aislamiento el dia: " + str(inicio.date()) + '.')
        pdf.drawString(110, 530, "Cumplira los 14 dias y finalizara su aislamiento obligatorio el " + str(fin.date()) + ' a las 6am.')
        pdf.save()
        # Nos movemos al comienzo del búfer StringIO
        packet.seek(0)
        nuevo_pdf = PdfFileReader(packet)
        # Leemos el pdf base
        existe_pdf = PdfFileReader(STATIC_ROOT+'/archivo/plantilla_alta.pdf', "rb")
        salida = PdfFileWriter()
        # Se agregan los datos de la persona que será dada de alta, al pdf ya existente
        pagina = existe_pdf.getPage(0)
        pagina.mergePage(nuevo_pdf.getPage(0))
        salida.addPage(pagina)
        # Finalmente se escribe la salida, en un archivo real
        path = MEDIA_ROOT+'/informacion/altas/'+individuo.num_doc+'_'+str(inicio)+".pdf"
        outputStream = open(path, "wb")
        salida.write(outputStream)
        outputStream.close()
        #Devolvemos el archivo para guardar:
        return '/informacion/altas/'+individuo.num_doc+'_'+str(inicio)+".pdf"
    except:
        logger.info("No se creo PDF para: " + str(individuo))
        logger.info("Motivo: " + str(traceback.format_exc()))

def realizar_alta_seguimiento(individuo, operador):
    #Generar documento de alta de aislamiento:
    doc = Documento(individuo=individuo)
    doc.tipo = 'AC'
    doc.archivo.name = creamos_doc_alta_seguimiento(individuo)
    doc.save()
    #Lo quitamos de Seguimiento Epidemiologico
    seguimiento = Seguimiento(individuo=individuo)
    seguimiento.tipo = 'FS'
    seguimiento.aclaracion = "Baja confirmada por: " + str(operador)
    seguimiento.save()
    #Lo damos de Alta de Aislamiento
    situacion = Situacion(individuo=individuo)
    seguimiento.aclaracion = "Baja confirmada por: " + str(operador)
    situacion.save()
    #Le damos de baja el seguimiento de tracking si tenia:
    for geoperador in individuo.geoperadores.all():
        geoperadores.del_trackeado(individuo)
    desactivar_tracking(individuo)
    #Generamos final tracking > Seguimiento
    seguimiento = Seguimiento(individuo=individuo)
    seguimiento.tipo = 'FT'
    seguimiento.aclaracion = "Baja confirmada por: " + str(operador)
    seguimiento.save()
    #Le cambiamos el domicilio a uno que no sea de aislamiento
    if individuo.domicilio_actual:#Si tiene domicilio actual
        if individuo.domicilio_actual.ubicacion:#Solo Si es un alojamiento
            dom = individuo.domicilios.filter(ubicacion=None).last()#Buscamos el ultimo conocido comun
            if not dom:#Si no existe
                dom = individuo.domicilio_actual#usamos el de aislamiento
                dom.ubicacion = None#Pero blanqueado
                #dom.aislamiento = False
                dom.tipo = "HO"
                dom.numero += '(pk:' + str(individuo.pk) + ')'#Agregamos 'salt' para evitar relaciones
            #Blanqueamos campos para crearlo como nuevo:
            dom.pk = None
            dom.aclaracion = "Baja confirmada por: " + str(operador)
            dom.fecha = timezone.now()
            dom.save()

def creamos_doc_alta_medica(seguimiento):
    try:
        #Obtenemos informacion inicial
        individuo = seguimiento.individuo
        operador = seguimiento.operador
        matricula = Atributo.objects.filter(individuo__num_doc=operador.num_doc, tipo="PM").last()
        fecha_alta = seguimiento.fecha.date()
        #Se crea un pdf utilizando reportLab
        packet = io.BytesIO()
        pdf = canvas.Canvas(packet, pagesize = A4)
        pdf.setFont('Times-Roman', 12)
        #Se escriben bloques de texto:        
        pdf.drawString(100, 660, individuo.apellidos + ', ' + individuo.nombres)
        pdf.drawString(150, 635, individuo.num_doc)
        pdf.drawString(150, 607, str(fecha_alta))
        pdf.drawString(350, 200, matricula.individuo.apellidos + ', ' + matricula.individuo.nombres)
        pdf.drawString(350, 180, 'M.N:' + matricula.aclaracion)
        pdf.save()
        # Nos movemos al comienzo del búfer StringIO
        packet.seek(0)
        nuevo_pdf = PdfFileReader(packet)
        # Leemos el pdf base
        existe_pdf = PdfFileReader(STATIC_ROOT+'/archivo/alta_medica.pdf', "rb")
        salida = PdfFileWriter()
        # Se agregan los datos de la persona que será dada de alta, al pdf ya existente
        pagina = existe_pdf.getPage(0)
        pagina.mergePage(nuevo_pdf.getPage(0))
        salida.addPage(pagina)
        # Finalmente se escribe la salida, en un archivo real
        path = MEDIA_ROOT+'/informacion/altamedica/'+individuo.num_doc+'_'+str(fecha_alta)+".pdf"
        outputStream = open(path, "wb")
        salida.write(outputStream)
        outputStream.close()
        #Devolvemos el archivo para guardar:
        return '/informacion/altamedica/'+individuo.num_doc+'_'+str(fecha_alta)+".pdf"
    except:
        logger.info("No se creo PDF para: " + str(individuo))
        logger.info("Motivo: " + str(traceback.format_exc()))

def es_operador_activo(num_doc):
    #Buscamos la cache
    operadores_activos = cache.get("operadores_activos")
    #Si no hay cache disponible
    if not operadores_activos:
        operadores_activos = []#Creamos nuevo grupo de registros
        operativos = OperativoVehicular.objects.all()#filter()
        operativos = operativos.prefetch_related('cazadores')
        for operativo in operativos:
            for cazador in operativo.cazadores.all():
                operadores_activos.append(cazador.num_doc)
        #Guardamos la cache
        cache.set("operadores_activos", operadores_activos, timeout=60)
    #Vemos si es cazador:
    if str(num_doc) in operadores_activos:
        return True

def obtener_operativo(num_doc):
    operativos = OperativoVehicular.objects.filter(cazadores__num_doc=num_doc)
    operativos = operativos.filter(estado='I')
    return operativos.last()