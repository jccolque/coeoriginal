#Imports de python
import json
import requests
#Imports django
from django.core.cache import cache
#Imports de la app
from .apps import CoreConfig


#Funciones para asignar a las app.configs    
def agregar_menu(app):
    CoreConfig.ADMIN_MENU += [(app.name.capitalize() , app.name)]

#def agregar_user_admin(app):
#    #Delegamos el manejo de usuarios
#    from app.models import Administrador
#    CoreConfig.ADMIN_MODELS[app.name.capitalize()] = Administrador

def obtener_organismos():#Funcion que obtiene del sistema de organigrama los organismos disponibles
    organismos = cache.get("organismos")
    if organismos is None:
        r = requests.get('http://organigrama.jujuy.gob.ar/ws_org/')
        orgs = json.loads(r.text)['data']
        organismos = list()
        for org in orgs:
            organismos.append((org['id'],org['nombre']))
        cache.set("organismos", organismos, 10 * 60)  # guardar la data por 10 minutos, y después sola expira
    return organismos