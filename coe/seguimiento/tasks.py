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
from georef.models import Nacionalidad, Departamento, Localidad
from informacion.models import Individuo
#Import Personales
from .models import Seguimiento

#Definimos logger
logger = logging.getLogger("tasks")

@background(schedule=1)
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
            #Aqui deberiamos generar el doc de baja de cuarentena
            #Generar documento al individuo tipo = ('AC', 'Certificado de Alta de Cuarentena'),
            #Mandar mail y dejar listo
        except Exception as error:
            logger.info("Fallo baja_aislamiento: " + str(individuo))
    logger.info("Finalizamos Baja de Seguimiento\n")