#Imports de Python
import io
#Imports de django
from django.core.files import File
from django.db.models import Q
#Imports Extras:
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
#Imports del Proyeto
from coe.settings import STATIC_ROOT, MEDIA_ROOT
from informacion.models import Individuo
#Imports de la app
from .models import Vigia

#Definimos funciones
def obtener_bajo_seguimiento():
    individuos = Individuo.objects.filter(Q(atributos__tipo='VE') | Q(situacion_actual__conducta__in=('D', 'E')))
    individuos = individuos.exclude(seguimientos__tipo='FS')
    individuos = individuos.distinct()
    return individuos

def creamos_doc_alta(individuo):
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