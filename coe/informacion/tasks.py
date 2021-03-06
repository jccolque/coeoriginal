#Traemos el sistema de Backgrounds
#Imports de Python
import logging
import traceback
from datetime import timedelta
#Imports django
from django.utils import timezone
from dateutil.relativedelta import relativedelta
#Imports extras
from background_task import background
#Imports del proyecto
from coe.constantes import DIAS_CUARENTENA
from background.functions import hasta_madrugada
from georef.models import Nacionalidad, Departamento, Localidad
from seguimiento.models import Seguimiento
#Import Personales
from .models import Archivo
from .models import Individuo, Domicilio
from .models import Situacion, Sintoma, Atributo

#Definimos logger
logger = logging.getLogger("tasks")

@background(schedule=hasta_madrugada(5))
def baja_aislamiento():
    logger.info(str(timezone.now())[0:16] + "\nIniciamos Baja de Aislamiento")
    #Obtenemos fecha de corte:
    fecha_corte = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtener aislados
    individuos = Individuo.objects.filter(situacion_actual__conducta='E')#Obtenemos a todos los aislados
    individuos = individuos.exclude(situacion_actual__fecha__gt=fecha_corte)#Evitamos a los que tienen que seguir aislados
    #Damos de baja el aislamiento
    for individuo in individuos:
        logger.info("Procesamos a: " + str(individuo))
        try:
            #Lo sacamos de aislamiento
            situacion = Situacion(individuo=individuo)
            situacion.estado = 11
            situacion.conducta = 'C'
            situacion.aclaracion = "Baja por Cumplimiento de Cuarentena"
            situacion.save()  #  Guardamos
        except Exception as error:
            logger.info("Fallo baja_aislamiento: " + str(individuo))
    logger.info("Finalizamos Baja de Aislamiento\n")

@background(schedule=hasta_madrugada(10))
def baja_cuarentena():
    logger.info(str(timezone.now())[0:16] + "\nIniciamos Baja de Cuarentena Obligatoria")
    #Obtenemos fecha de corte:
    fecha_corte = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtener aislados
    individuos = Individuo.objects.filter(situacion_actual__conducta='D')#Obtenemos a todos los aislados
    individuos = individuos.exclude(situacion_actual__fecha__gt=fecha_corte)#Evitamos a los que tienen que seguir en cuarentena
    #Damos de baja el aislamiento
    for individuo in individuos:
        logger.info("Procesamos a: " + str(individuo))
        try:
            #Lo sacamos de aislamiento
            situacion = Situacion(individuo=individuo)
            situacion.estado = 11
            situacion.conducta = 'C'
            situacion.aclaracion = "Baja por Cumplimiento de Cuarentena"
            situacion.save()  #  Guardamos
        except Exception as error:
            logger.info("Fallo baja_cuarentena de: " + str(individuo))
    logger.info("Finalizamos Baja de Cuarentena Obligatoria\n")

@background(schedule=hasta_madrugada(20))
def devolver_domicilio():
    logger.info(str(timezone.now())[0:16] + "\nIniciamos el Cambio de Domicilio")
    #Obtenemos fecha de corte:
    fecha_corte = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtener aislados
    individuos = Individuo.objects.filter(domicilio_actual__aislamiento=True)
    individuos = individuos.exclude(domicilio_actual__fecha__gt=fecha_corte)
    individuos = individuos.exclude(domicilio_actual__ubicacion=None)#Quitamos los que no estan en hoteles
    #Les buscamos posible nuevo domicilio
    for individuo in individuos:
        logger.info("Procesamos a: " + str(individuo))
        try:
            dom = individuo.domicilios.filter(aislamiento=False).last()
            #Si tiene un domicilio valido que no es de aislamiento
            if not dom:
                dom = individuo.domicilio_actual
                dom.ubicacion = None
                #dom.aislamiento = False
                dom.numero += '(pk:' + str(individuo.pk) + ')'
            #Blanqueamos campos para crearlo como nuevo:
            dom.pk = None
            dom.aclaracion = "Movido Automaticamente por final de Cuarentena."
            dom.fecha = timezone.now()
            dom.save()
        except Exception as error:
            logger.info("Fallo Cambio de Domicilio: " + str(individuo))
    logger.info("Finalizamos devoluciones a Domicilios\n")
