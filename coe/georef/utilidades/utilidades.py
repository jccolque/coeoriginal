#Imports de python
import json
import traceback
#Imports del proyecto
from core.api import requests_retry_session
from georef.models import Localidad, Departamento, Provincia
from georef.functions import obtener_argentina

#Definimos webservices origen:
def actualizar_infra_gob(filename):
    #Generamos datos existentes:
    argentina = obtener_argentina()
    provincias_cargados = {p.id_infragob: p for p in Provincia.objects.exclude(id_infragob=None)}
    departamentos_cargados = {d.id_infragob: d for d in Departamento.objects.exclude(id_infragob=None)}
    localidades_cargadas = {l.id_infragob: l for l in Localidad.objects.exclude(id_infragob=None)}
    print("Datos Pre Cargados")

    #Obtenemos web service
    #r = requests_retry_session().get('https://infra.datos.gob.ar/catalog/modernizacion/dataset/7/distribution/7.27/download/localidades-censales.json')
    #localidades = json.loads(r.text)['localidades-censales']

    #Recorremos el json
    with open(filename) as json_file:
        localidades_json = json.load(json_file)['localidades-censales']
        #Recorremos las localidades
        for loc_gob in localidades_json:
            #Si la tenemos la preparamos para actualizar
            if not loc_gob['id'] in localidades_cargadas:#Nos aseguramos de no crear de nuevo
                try:

                    #Obtenemos la provincia
                    if loc_gob['provincia']['id'] in provincias_cargados:
                        p = provincias_cargados[loc_gob['provincia']['id']]
                    else:
                        p = Provincia()
                        p.nombre = loc_gob['provincia']['nombre']
                        p.id_infragob = loc_gob['provincia']['id']
                        p.nacion = argentina
                        p.save()
                        provincias_cargados[p.id_infragob] = p
                        print("\nCreamos Provincia: " + p.nombre + "\n")

                    #Departamento:
                    if loc_gob['departamento']['id'] in departamentos_cargados:
                        d = departamentos_cargados[loc_gob['departamento']['id']]
                    else:
                        d = Departamento()
                        d.nombre = loc_gob['departamento']['nombre']
                        d.id_infragob = loc_gob['departamento']['id']
                        d.provincia = p
                        d.save()
                        print("\nCreamos Departamento: " + p.nombre + ', ' + d.nombre + "\n")

                    #Cargamos datos de localidades:
                    try:
                        l = Localidad()#Creamos una nueva
                        l.nombre = loc_gob['nombre']
                        l.id_infragob = loc_gob['id']
                        l.latitud = loc_gob['centroide']['lat']
                        l.longitud = loc_gob['centroide']['lon']
                        l.departamento = d
                        l.save()
                        print("Guardamos: "+ l.nombre + ', ' + d.nombre)
                    except:
                        print("No se pudo guardar Localidad: " + loc_gob['nombre'])

                except Exception as e:
                    #Si no se guardo decimos por que:
                    print("No se pudo procesar: " + loc_gob['nombre'])
                    print("Linea: " + str(loc_gob))
                    print('Error: '+ str(traceback.format_exc()))

            else:
                l = localidades_cargadas[loc_gob['id']]
                l.latitud = loc_gob['centroide']['lat']
                l.longitud = loc_gob['centroide']['lon']
                l.save()
                print("Actualizamos: " + l.nombre + ', ' + l.departamento.nombre)
