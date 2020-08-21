#Traemos el sistema de Backgrounds
#Imports de Python
import logging
import traceback
from datetime import datetime, timedelta
#Imports django
from django.utils import timezone
from dateutil.relativedelta import relativedelta
#Imports extras
from background_task import background
#Imports del proyecto
from coe.constantes import DIAS_CUARENTENA
from background.functions import hasta_madrugada
from georef.models import Nacionalidad, Departamento, Localidad
from informacion.models import Archivo
from informacion.models import Individuo, Domicilio
from operadores.models import Operador
#Import Personales
from .models import Seguimiento
from .models import Muestra
from .functions import realizar_alta

#Definimos logger
logger = logging.getLogger("tasks")

@background(schedule=hasta_madrugada(5))
def baja_seguimiento():
    logger.info(str(timezone.now())[0:16] + "\nIniciamos Baja de Seguimiento")
    #Obtenemos fecha de corte:
    fecha_corte = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtenemos seguimientos iniciados antes de la fecha de corte
    seguimientos = Seguimiento.objects.filter(tipo='I', fecha__lt=fecha_corte)
    #Obtenemos todos los individuos seguidos
    individuos = Individuo.objects.filter(seguimientos__in=seguimientos).distinct()
    #Excluimos todos los ya dados de baja:
    individuos = individuos.exclude(seguimientos__tipo='FS')    
    #Los damos de baja
    for individuo in individuos:
        logger.info("Procesamos a: " + str(individuo))
        try:
            seguimiento = Seguimiento(individuo=individuo)
            seguimiento.tipo = 'FS'
            seguimiento.aclaracion = "Baja automatica por cumplir tiempo de cuarentena"
            seguimiento.save()
        except Exception as error:
            logger.info("Fallo baja_aislamiento: " + str(individuo))
    logger.info("Finalizamos Baja de Seguimiento\n")

@background(schedule=5)#Debe ser a pedido
def altas_masivas(inds_ids, operador_id):
    #Obtenemos todos los individuos
    individuos = Individuo.objects.filter(id__in=inds_ids)
    operador = Operador.objects.get(pk=operador_id)
    for individuo in individuos:
        realizar_alta(individuo, operador)

@background(schedule=5)#
def guardar_muestras_bg(lineas, archivo_id, ultimo=False):
    logger.info("Iniciamos CARGA MASIVA DE PRUEBAS")
    #Obtenemos archivo sobre el que vamos generando el update:
    archivo = Archivo.objects.get(pk=archivo_id)
    if not archivo.descripcion:#Si es el primer bloque:
        archivo.descripcion = "<h3>Inicia la Carga Masiva de Muestras: "+str(timezone.now())+"</h3>"
    #Generamos elementos basicos:
    num_docs_existentes = {i.num_doc: i for i in Individuo.objects.all()}#Obtenemos dni existentes
    san_salvador = Localidad.objects.get(id_infragob=38021060)
    dict_locs = {i.nombre: i for i in Localidad.objects.filter(departamento__provincia__id_infragob=38)}#Son Standards: Jujuy
    #GEneramos todos los elementos nuevos
    muestras = []
    archivo.descripcion += "<li> Inicio de Procesamiento: "+ str(timezone.now())+"</li>"
    archivo.descripcion += "<p>Cantidad Lineas: "+str(len(lineas))+"</p>"
    for linea in lineas:
        linea = linea.split(';')
        if linea[0]:
            #Si el individuo no existe en la db:
            if linea[4] not in num_docs_existentes:
                #Creamos nuevo individuo                          
                nuevo_individuo = Individuo()
                nuevo_individuo.nombres = linea[2]
                nuevo_individuo.apellidos = linea[3]
                nuevo_individuo.num_doc = linea[4]
                nuevo_individuo.sexo = linea[5]
                nuevo_individuo.save()
                #Creamos Domicilio
                domicilio = Domicilio()
                domicilio.calle = linea[19]
                domicilio.numero = linea[20]
                domicilio.individuo = nuevo_individuo
                if linea[11] in dict_locs:
                    domicilio.localidad = dict_locs[linea[11]] 
                else:
                    domicilio.localidad = san_salvador#Hardcodeamos capital
                domicilio.save()
            else:
                nuevo_individuo = num_docs_existentes[linea[4]]
            #Creamos muestra
            muestra = Muestra()
            muestra.edad = linea[6]
            fecha = datetime.strptime(linea[13], '%d/%m/%Y').date()
            muestra.fecha_muestra = fecha            
            muestra.grupo_etereo = linea[18]
            muestra.individuo = nuevo_individuo
            muestras.append(muestra)    
    #Creamos este bloque
    Muestra.objects.bulk_create(muestras)
    archivo.descripcion += "<li>Guardado Fragmento: "+ str(timezone.now())+"</li>"
    archivo.save()
    if ultimo:
        archivo.descripcion += "<p>FIN ARCHIVO</p>"
        archivo.procesado = True
        archivo.save()
    logger.info("Finalizamos carga de muestras Masiva.\n")