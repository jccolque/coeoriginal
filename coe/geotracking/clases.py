#Imports de python
import json
#Imports del proyecto
from informacion.models import Individuo

#Definimos clases para hacer cosas:
class MapeadorIndividual:
    def __init__(self, individuo):
        self.individuo = individuo
        #Iniciamos procesamiento:
        self.trackeado = individuo.geoposiciones.filter(tipo='ST').exists()
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
        #imagenes:
        data["fotografia"] = self.individuo.get_foto()
        documentos = self.individuo.get_dnis()

        # doc.tipo == 'DI'
        # aclracion__icontains frente o reverso

        if documentos:
            try:
                data["DNI_Front"] = documentos[0].archivo.url
                data["DNI_Back"] = documentos[-1].archivo.url
            except:
                pass
        #Domicilio:
        data["domicilio"] = self.individuo.domicilio_actual.calle + ' ' + self.individuo.domicilio_actual.numero
        data["localidad"] = str(self.individuo.domicilio_actual.localidad)
        #Parametros:
        data["registro_app"] = str(self.parametros.fecha)
        data["intervalo"] = self.parametros.intervalo
        data["radio1"] = self.parametros.distancia_alerta
        data["radio2"] = self.parametros.distancia_critica
        #Base:
        if self.gps_base:
            data["punto_base"] = True
            data["base_latitud"] = self.gps_base.latitud
            data["base_longitud"] = self.gps_base.longitud
        else:
            data["punto_base"] = False
            data["base_latitud"] = 0
            data["base_longitud"] = 0
        #Geoposiciones
        data["geoposiciones"] = []
        geoposiciones = self.individuo.geoposiciones.exclude(tipo='PC')
        for geopos in geoposiciones:
            #Creamos cada dict por posicion a mostrar:
            gpd = {}
            gpd["tipo"] = geopos.get_tipo_display()
            gpd["fecha"] = str(geopos.fecha.date())
            gpd["hora"] = str(geopos.fecha.time())
            gpd["latitud"] = geopos.latitud
            gpd["longitud"] = geopos.longitud
            gpd["distancia"] = geopos.distancia
            gpd["aclaracion"] = geopos.aclaracion
            gpd["procesada"] = geopos.procesada
            gpd["operador"] = str(geopos.operador)
            gpd["icono"] = geopos.icono()
            #Lo sumamos al grupo de geopos
            data["geoposiciones"].append(gpd)
        #Entregamos el diccionario terminado
        return data