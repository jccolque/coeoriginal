#Imports de Python
from datetime import timedelta
#Imports django
from django.db.models import Q
from django.utils import timezone
#Imports Extras
from background_task import background
#Imports del proyeco
#Import de la app
from .geofence import obtener_trackeados

#Definimos tareas
@background(schedule=1)
def geotrack_sin_actualizacion():
    print("Lanzamos Background job de geotracking")
    individuos = obtener_trackeados()
    #Quitamos los que enviaron Posicion GPS en la ultima hora:
    limite = timezone.now() - timedelta(hours=1)
    individuos = individuos.exclude(Q(geoposiciones__fecha__gt=limite, geoposiciones__tipo='RG'))
    #Quitamos los que ya fueron infomados
    #individuos = individuos.exclude(Q(geoposiciones__alerta='FG', geoposiciones__procesada=True))
    #Recorrer y alertar
    for individuo in individuos:
        geopos = individuo.geoposicion()
        geopos.alerta = 'FG'
        geopos.procesada = False
        horas = int((geopos.fecha - timezone.now()).seconds / 3600)
        geopos.aclaracion = "Lleva " + str(horas) + "hrs sin informar posicion."
        geopos.save()