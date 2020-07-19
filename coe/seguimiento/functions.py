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
from coe.constantes import DIAS_CUARENTENA
from informacion.models import Individuo, Situacion, Documento
from app.functions import desactivar_tracking
#Imports de la app
from .models import Seguimiento
from .models import Vigia, OperativoVehicular

#Logger
logger = logging.getLogger('errors')

#Definimos funciones
def obtener_bajo_seguimiento():
    individuos = Individuo.objects.filter(situacion_actual__conducta__in=('D', 'E'))
    return individuos

def creamos_doc_alta(individuo):
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
        path = MEDIA_ROOT+'/informacion/altas/'+individuo.num_doc+".pdf"
        outputStream = open(path, "wb")
        salida.write(outputStream)
        outputStream.close()
        #Devolvemos el archivo para guardar:
        return '/informacion/altas/'+individuo.num_doc+".pdf"
    except:
        logger.info("No se creo PDF para: " + str(individuo))
        logger.info("Motivo: " + str(traceback.format_exc()))

def crear_doc_descartado(individuo):
    try:
        packet = io.BytesIO()
        #Se crea un pdf utilizando reportLab
        pdf = canvas.Canvas(packet, pagesize = A4)
        pdf.setFont('Times-Roman', 13)
        pdf.drawString(85, 635, individuo.apellidos + ', ' + individuo.nombres + ' - ' + individuo.get_tipo_doc_display() + ': ' + str(individuo.num_doc))
        pdf.setFont('Times-Roman', 16)
        pdf.drawString(250, 115, str(timezone.now().date()))
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
        path = MEDIA_ROOT+'/informacion/descartado/'+individuo.num_doc+".pdf"
        outputStream = open(path, "wb")
        salida.write(outputStream)
        outputStream.close()
        #Devolvemos el archivo para guardar:
        return '/informacion/descartado/'+individuo.num_doc+".pdf"
    except:
        logger.info("No se creo PDF para: " + str(individuo))
        logger.info("Motivo: " + str(traceback.format_exc()))

def realizar_alta(individuo, operador):
    #Generar documento de alta de aislamiento:
    doc = Documento(individuo=individuo)
    doc.tipo = 'AC'
    doc.archivo.name = creamos_doc_alta(individuo)
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
    individuo.geoperadores.clear()
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
                dom.aislamiento = False
                dom.numero += '(pk:' + str(individuo.pk) + ')'#Agregamos 'salt' para evitar relaciones
            #Blanqueamos campos para crearlo como nuevo:
            dom.pk = None
            dom.aclaracion = "Baja confirmada por: " + str(operador)
            dom.fecha = timezone.now()
            dom.save()

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

def asignar_vigilante(individuo, tipo):
    #Iniciamos proceso de asignacion:
    try:
        if not individuo.vigiladores.filter(tipo=tipo).exists():#Si no tiene Vigilante
            #Intentamos buscarle el vigilante que menos asignados tenga
            vigias = Vigia.objects.filter(tipo=tipo).annotate(cantidad=Count('controlados'))
            for vigia in vigias.order_by('cantidad'):
                if vigia.max_controlados > vigia.cantidad:
                    vigia.controlados.add(individuo)
                    #Si no es mental o circulacion, lo dejamos solo en ese panel nuevo:
                    if tipo not in  ("VM", "VT"):
                        for old_vigilante in individuo.vigiladores.exclude(tipo__in=("VM", "VT")).exclude(id=vigia.id):
                            individuo.vigiladores.remove(old_vigilante)
                    break#Lo cargamos, limpiamos, terminamos
    except:
        logger.info("No existen Vigias: " + tipo + ", " + str(individuo) + " quedo sin vigilancia.")