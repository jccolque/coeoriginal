#Imports de Python
import io
import logging
import traceback
#Imports de django
from django.utils import timezone
from django.core.files import File
from django.db.models import Q
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
from seguimiento.models import Seguimiento
#Imports de la app
from .models import Vigia

#Logger
logger = logging.getLogger('errors')

#Definimos funciones
def obtener_bajo_seguimiento():
    individuos = Individuo.objects.filter(situacion_actual__conducta__in=('D', 'E'))
    individuos = individuos.exclude(seguimientos__tipo='FS')
    return individuos

def creamos_doc_alta(individuo):
    try:
        packet = io.BytesIO()
        #Se crea un pdf utilizando reportLab
        pdf = canvas.Canvas(packet, pagesize = A4)
        pdf.setFont('Times-Roman', 12)
        pdf.drawString(85, 635, individuo.apellidos + ', ' + individuo.nombres + ' - ' + individuo.get_tipo_doc_display() + ': ' + str(individuo.num_doc))
        pdf.drawString(85, 620, "Inicio Su Aislamiento el dia: " + str(individuo.situaciones.filter(conducta__in=('D','E')).last().fecha.date()) + '.')
        pdf.save()
        # Nos movemos al comienzo del búfer StringIO
        packet.seek(0)
        nuevo_pdf = PdfFileReader(packet)
        # Leemos el pdf base
        existe_pdf = PdfFileReader(STATIC_ROOT+'/archivo/plantilla_aislamiento.pdf', "rb")
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
    #Lo sacamos de los panel:
    vigiladores = individuo.vigiladores.all()
    individuo.vigiladores.clear()
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