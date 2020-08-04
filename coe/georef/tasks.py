#Imports de python
import json
import logging
import traceback
#Imports Extras
from background_task import background
#Imports del proyecto
from core.api import requests_retry_session
from background.functions import hasta_madrugada
#Imports de la app
from .models import Provincia, Departamento, Localidad
from .functions import obtener_argentina

#Definimos logger
logger = logging.getLogger("tasks")

#Definimos webservices origen:
@background(schedule=0)
def obtener_localidades_infra_gob():
    logger.info("Iniciamos proceso de carga de datos geograficos:")
    #Obtenemos web service
    r = requests_retry_session().get('https://infra.datos.gob.ar/catalog/modernizacion/dataset/7/distribution/7.27/download/localidades-censales.json')
    logger.info("Json Descargado")
    localidades_json = json.loads(r.text)['localidades-censales']
    logger.info("Json Procesado")

    #Obtenemos datos basicos:
    argentina = obtener_argentina()
    provincias = {p.id_infragob: p for p in Provincia.objects.exclude(id_infragob=None)}
    departamentos = {d.id_infragob: d for d in Departamento.objects.exclude(id_infragob=None)}
    localidades = {l.id_infragob: l for l in Localidad.objects.exclude(id_infragob=None)}
    logger.info("Obtuvimos diccionarios pre existentes")

    #Recorremos Json creando localidades
    for loc_gob in localidades_json['localidades-censales']:
        #Creamos Provincia:
        if loc_gob['provincia']['id'] in provincias:
            p = provincias[loc_gob['provincia']['id']]
        else:
            p = Provincia()
            p.nombre = loc_gob['provincia']['nombre']
            p.id_infragob = loc_gob['provincia']['id']
            p.nacion = argentina
            p.save()
            provincias[p.id_infragob] = p
            logger.info("Creamos Provincia: " + str(p))

        #Creamos Departamento:
        if loc_gob['departamento']['id'] in departamentos:
            d = departamentos[loc_gob['provincia']['id']]
        else:
            d = Departamento()
            d.nombre = loc_gob['departamento']['nombre']
            d.id_infragob = loc_gob['departamento']['id']
            d.provincia = p
            d.save()
            departamentos[d.id_infragob] = d
            logger.info("Creamos Departamento: " + str(d))

        #Creamos localidad
        if not loc_gob['id'] in localidades:
            l = Localidad()
            l.nombre = loc_gob['nombre']
            l.id_infragob = loc_gob['id']
            l.latitud = loc_gob['centroide']['lat']
            l.longitud = loc_gob['centroide']['lon']
            l.save()
            logger.info("Creamos Localidad: " + str(l))