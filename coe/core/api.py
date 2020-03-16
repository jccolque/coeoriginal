#Imports Python
import json
import requests 
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
#Imports Django
from django.core.cache import cache
from django.db import models
#Imports de la app

#Definimos modelo necesario para funcion

#Funcion Generica
def requests_retry_session(
        retries=5,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
    ):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

#Funciones API
def obtener_organismos():
    organismos = cache.get("organismos")
    if not organismos:
        r = requests_retry_session().get('http://organigrama.jujuy.gob.ar/ws_org/')
        orgs = json.loads(r.text)['data']
        organismos = list()
        for org in orgs:
            organismos.append((org['id'],org['nombre']))
        cache.set("organismos", organismos)
    return organismos

def org_id_from_name(nombre):
    organismos = obtener_organismos()
    for organismo in organismos:
        if nombre == organismo[1]:
            return organismo[0]
    return ''