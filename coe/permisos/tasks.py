#Imports de Python
import logging
import traceback
from datetime import timedelta
#Imports django
from django.utils import timezone
#Imports Extras
from background_task import background
#Imports del proyeco
#Import de la app
from .models import IngresoProvincia

#Definimos logger
logger = logging.getLogger("tasks")

#Definimos tareas
@background(schedule=3)
def eliminar_ingresos_provinciales():
    logger.info("\neliminar_ingresos_provinciales")
    #Buscamos los recien cargados
    ingresos = IngresoProvincia.objects.filter(estado='C')
    #Filtramos los que se tienen que ir
    limite = timezone.now() - timedelta(days=3)
    ingresos = ingresos.filter(fecha__lt=limite)
    for ingreso in ingresos:
        ingreso.estado = 'B'
        ingreso.save()
        logger.info("Dimos de baja pedido " + ingreso.patente)
    logger.info("Finalizamos: eliminar_ingresos_provinciales")