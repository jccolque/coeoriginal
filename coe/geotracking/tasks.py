#Imports de Python
from datetime import timedelta
#Imports django
from django.db.models import Q
from django.utils import timezone
#Imports Extras
from background_task import background
#Imports del proyeco
from informacion.models import Seguimiento
from app.models import AppNotificacion
#Import de la app
from .models import GeoPosicion
from .geofence import obtener_trackeados

#Definimos tareas
@background(schedule=1)
def geotrack_sin_actualizacion():
    individuos = obtener_trackeados()
    #Quitamos los que enviaron Posicion GPS en la ultima hora:
    limite = timezone.now() - timedelta(hours=1)
    individuos = individuos.exclude(geoposiciones__in=GeoPosicion.objects.filter(fecha__gt=limite, tipo='RG'))
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

@background(schedule=1)
def finalizar_geotracking():
    individuos = obtener_trackeados()
    #Obtenemos los que estan siendo trackeados hace mas de 14 dias:
    inicio = timezone.now() - timedelta(days=14)
    individuos = individuos.filter(geoposiciones__in=GeoPosicion.objects.filter(tipo='ST', fecha__lt=inicio)).distinct()
    #Tenemos en cuenta los que le reiniciaron el geotracking
    individuos = individuos.exclude(geoposiciones__in=GeoPosicion.objects.filter(tipo='ST', fecha__gt=inicio))
    #Los damos de baja:
    for individuo in individuos:
        print("Baja para: "+str(individuo))
        st_geopos = individuo.filter(tipo='ST').last()
        #Generamos seguimiento de Fin de Tracking
        seguimiento = Seguimiento(individuo=individuo)
        seguimiento.tipo = 'FT'
        seguimiento.aclaracion = "Fin de Seguimiento iniciado el: " + str(st_geopos.fecha)[0:16]
        print(seguimiento)#seguimiento.save()
        #Enviamos pushnotification para dar de baja tracking
        notif = AppNotificacion()
        notif.appdata = individuo.appdata
        notif.titulo = 'Finalizo su periodo bajo Supervicion Digital'
        notif.mensaje = 'Se han cumplido los 14 dias de seguimiento.'
        notif.accion = 'ST'
        print(notif)#notif.save()#Al grabar el local, se envia automaticamente por firebase
        #Lo aliminamos de los seguimientos
        print("Eliminamos controles")#individuo.geoperadores.clear()
