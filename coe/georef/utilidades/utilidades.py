#Imports de python
import json
import traceback
#Imports del proyecto
from core.api import requests_retry_session
from georef.models import Localidad, Departamento, Provincia
from georef.functions import obtener_argentina

#Definimos webservices origen:
def actualizar_infra_gob(filename=None):
    #Iniciamos contadores:
    locs_creadas = 0
    locs_actualizadas = 0
    falla_critica = 0
    #Iniciamos log:
    fallas = []
    #Iniciamos proceso
    print("Iniciamos Proceso de Carga de Datos de Infra.Gob.Ar")
    #Generamos datos existentes:
    argentina = obtener_argentina()
    provincias_cargados = {p.id_infragob: p for p in Provincia.objects.exclude(id_infragob=None)}
    departamentos_cargados = {d.id_infragob: d for d in Departamento.objects.exclude(id_infragob=None)}
    localidades_cargadas = {l.id_infragob: l for l in Localidad.objects.exclude(id_infragob=None)}
    print("Datos Existentes Pre Cargados")
    print(str(len(localidades_cargadas)) + "Localidades Cargadas.")

    if not filename:#Si no es un archivo fisico
        #Obtenemos web service
        print("Iniciamos descarga desde internet")
        r = requests_retry_session().get('https://infra.datos.gob.ar/catalog/modernizacion/dataset/7/distribution/7.27/download/localidades-censales.json')
        print("Iniciamos procesamiento de Json")
        localidades_json = json.loads(r.text)['localidades-censales']
    else:
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
                #Chequeamos que no este en la DB sin la id
                elif Provincia.objects.filter(nombre__icontains=loc_gob['provincia']['nombre']).exists():
                    p = Provincia.objects.filter(nombre__icontains=loc_gob['provincia']['nombre']).first()
                    p.id_infragob = loc_gob['provincia']['id']
                    p.save()
                    provincias_cargados[p.id_infragob] = p
                    print("Actualizamos Provincia: " + p.nombre)
                else:
                    try:#Lo creamos
                        p = Provincia()
                        p.nombre = loc_gob['provincia']['nombre']
                        p.id_infragob = loc_gob['provincia']['id']
                        p.nacion = argentina
                        p.save()
                        provincias_cargados[p.id_infragob] = p
                        print("Creamos Provincia: " + p.nombre)
                    except:
                        print("No se pudo Crear Provincia: " + p.nombre)

                #Departamento:
                if loc_gob['departamento']['id'] in departamentos_cargados:
                    d = departamentos_cargados[loc_gob['departamento']['id']]
                #Chequeamos que no este en la DB sin la id
                elif Departamento.objects.filter(nombre=loc_gob['departamento']['nombre'], provincia=p).exists():
                    d = Departamento.objects.filter(nombre=loc_gob['departamento']['nombre'], provincia=p).first()
                    d.id_infragob = loc_gob['departamento']['id']
                    d.save()
                    departamentos_cargados[d.id_infragob] = d
                    print("Actualizamos Departamento: " + p.nombre)
                else:
                    try:
                        d = Departamento()
                        d.nombre = loc_gob['departamento']['nombre']
                        d.id_infragob = loc_gob['departamento']['id']
                        d.provincia = p
                        d.save()
                        departamentos_cargados[d.id_infragob] = d
                        print("Creamos Departamento: " + p.nombre + ', ' + d.nombre)
                    except:
                        print("No se pudo guardar Departamento: " + p.nombre + ', ' + d.nombre)

                #Cargamos datos de localidades:
                l = Localidad.objects.filter(nombre=loc_gob['nombre'], departamento=d).last()
                if not l:
                    l = Localidad()#Creamos una nueva
                try:
                    l = Localidad()#Creamos una nueva
                    l.nombre = loc_gob['nombre']
                    l.id_infragob = loc_gob['id']
                    l.latitud = loc_gob['centroide']['lat']
                    l.longitud = loc_gob['centroide']['lon']
                    l.departamento = d
                    l.save()
                    locs_creadas+= 1
                    print("Creamos Localidad: "+ l.nombre + ', ' + d.nombre)
                except:
                    print("No se pudo guardar Localidad: " + loc_gob['nombre'])

            except Exception as e:
                #Si no se guardo decimos por que:
                falla_critica+= 1
                fallas.append([e, traceback.format_exc()])
        #Si la encontramos: Actualizamos
        else:
            l = localidades_cargadas[loc_gob['id']]
            l.latitud = loc_gob['centroide']['lat']
            l.longitud = loc_gob['centroide']['lon']
            l.save()
            locs_actualizadas+= 1
            print("Actualizamos: " + l.nombre + ', ' + l.departamento.nombre)

    #Informamos:
    print("\nResultados:")
    print("Localidades Creadas:" + str(locs_creadas))
    print("Localidades Actualizadas: " + str(locs_actualizadas))
    print("Errores Criticos: " + str(falla_critica))
    return fallas