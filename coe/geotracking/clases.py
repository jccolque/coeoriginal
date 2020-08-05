#Imports de python
import json
from datetime import timedelta
#Imports del proyecto
from informacion.models import Individuo

#Definimos clases para hacer cosas:
class MapeadorIndividual:
    def __init__(self, individuo):
        self.individuo = individuo
        #Iniciamos procesamiento:
        self.trackeado = individuo.geoposiciones.filter(tipo__in=('ST','PC')).exists()
        self.fotografia = self.individuo.get_foto()
        #Documentos:
        self.documentos = self.individuo.get_dnis()
        if self.documentos:
            self.dni_frente = self.documentos[0].archivo.url
            self.dni_reverso = self.documentos[-1].archivo.url
        #Tracking info
        if self.trackeado:#Si esta persona fue trackeada
            self.parametros = individuo.appdata
            self.gps_base = individuo.geoposiciones.filter(tipo='PC').last()
    
    def create_dict(self):
        data = {}
        #Basico:
        data["id"] = self.individuo.pk
        data["num_doc"] = self.individuo.num_doc
        data["apellidos"] = self.individuo.apellidos
        data["situacion"] = str(self.individuo.get_situacion())
        data["nombres"] = self.individuo.nombres
        data["telefono"] = self.individuo.telefono
        #Domicilio:
        data["domicilio"] = self.individuo.domicilio_actual.calle + ' ' + self.individuo.domicilio_actual.numero
        data["localidad"] = str(self.individuo.domicilio_actual.localidad)
        #Parametros:
        if self.parametros:
            data["registro_app"] = str(self.parametros.fecha)
            data["intervalo"] = self.parametros.intervalo
            data["radio1"] = self.parametros.distancia_alerta
            data["radio2"] = self.parametros.distancia_critica
        #Base:
        if self.gps_base:
            data["punto_base"] = 1
            data["base_latitud"] = float(self.gps_base.latitud)
            data["base_longitud"] = float(self.gps_base.longitud)
        else:
            #Si no tiene punto base buscamos otro:
            gps = self.individuo.geoposiciones.last()
            data["base_latitud"] = float(gps.latitud)
            data["base_longitud"] = float(gps.longitud)

        #Geoposiciones
        data["geoposiciones"] = []
        geoposiciones = self.individuo.geoposiciones.all()
        #Hacemos ciertos filtros para optimizar:
        #if geoposiciones.exclude(alerta="SA").filter(procesada=False).exists():
        #    geoposiciones = geoposiciones.exclude(tipo="RG", alerta="SA")
        #Creamos cada entrada del dict por posicion a mostrar:
        geoposiciones = geoposiciones.order_by("-fecha")
        for geopos in geoposiciones:
            gpd = {}
            gpd["id"] = geopos.id
            gpd["tipo"] = geopos.get_tipo_display()
            fecha = geopos.fecha - timedelta(hours=3)#ODIO HARDCODEAR
            gpd["fecha"] = str(fecha.date())
            gpd["hora"] = str(fecha.time())
            gpd["latitud"] = float(geopos.latitud)
            gpd["longitud"] = float(geopos.longitud)
            gpd["distancia"] = int(geopos.distancia)
            gpd["talerta"] = geopos.alerta
            gpd["alerta"] = geopos.get_alerta_display()
            gpd["aclaracion"] = geopos.aclaracion
            gpd["procesada"] = str(geopos.procesada)
            gpd["operador"] = str(geopos.operador)
            gpd["icono"] = geopos.icono()
            #Lo sumamos al grupo de geopos
            data["geoposiciones"].append(gpd)
        #Entregamos el diccionario terminado
        return data