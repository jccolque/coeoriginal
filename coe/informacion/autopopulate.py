#Imports django
from django.utils import timezone
from georef.models import Nacionalidad, Departamento, Localidad
#Imports de la app
from .models import Individuo, Domicilio

def upload_padron(filename):
    print("Carga Masiva de Padron: ", timezone.now())
    num_lines = sum(1 for line in open(filename))
    print("Cantidad de Lineas: ", num_lines)
    with open(filename, encoding="utf8") as lines:
        #Limpiamos la base de datos:
        print("Eliminamos cargados de ultimo Padron: ", timezone.now())
        Individuo.objects.filter(observaciones="PADRON").delete()
        print("Generando Individuos Existentes: ", timezone.now())
        num_docs_existentes = [i.num_doc for i in Individuo.objects.all()]
        #Generamos elementos basicos:
        nac = Nacionalidad.objects.get_or_create(nombre="Argentina")[0]
        #Indexamos todas las localidades:
        localidades = {l.nombre: l for l in Localidad.objects.all()}
        #GEneramos todos los elementos nuevos
        individuos = []
        print("Inicio de Procesamiento: ", timezone.now())
        mod = int(num_lines / 100)
        count = 0
        for linea in lines:
            count += 1
            if count % mod == 0:
                print("Procesado: ", int(count/mod), "%")
                #Guardamos y generamos ids
                if (count % (mod * 5)) == 0:
                    print("Se guardaran:", len(individuos), "Individuos.")
                    Individuo.objects.bulk_create(individuos)#Guardamos de a fragmentos para que no explote
                    individuos = []
                    print("Guardando Fragmento: ", timezone.now())
            #procesamos cada linea
            linea = linea.split(',')
            if linea[0]:
            #Instanciamos individuos
                individuo = Individuo()                        
                individuo.tipo_doc = 2
                individuo.num_doc = linea[0]
                individuo.apellidos = linea[1]
                individuo.nombres = linea[2]
                individuo.nacionalidad = nac #Todos Argentinos
                individuo.observaciones = "PADRON"
                #Cacheamos localidades inexistentes:
                if linea[4] not in localidades:
                    print("Se creo: ", linea[4], '| Hay que Corregir el Departamento.')
                    localidad = Localidad()
                    localidad.departamento = Departamento.objects.first()
                    localidad.nombre = linea[4]
                    localidad.save()
                    localidades[localidad.nombre] = localidad
                #Lo agregamos a la lista
                if individuo.num_doc not in num_docs_existentes:
                    num_docs_existentes.append(individuo.num_doc)
                    individuos.append(individuo)
        print("Se termino de crear la lista inicial de individuos")
        print("Cantidad de Individuos Procesados:", len(individuos))
        #Indexamos id:individuos en un dict
        individuos = {i.num_doc: i for i in Individuo.objects.all()}
        #Cargamos domicilios
        print("Comenzamos a cargar Domicilios", timezone.now())
        domicilios = []
        count = 0
        for linea in lines:#Agregamos los domicilios
            count += 1
            if count % mod == 0:
                print("Procesado: ", int(count/mod), "%")
                #Guardamos y generamos ids
                if (count % (mod * 5)) == 0:
                    Domicilio.objects.bulk_create(domicilios)#Guardamos de a fragmentos para que no explote
                    domicilios = []#limpiamos lo ya guardado
                    print("Guardando Fragmento: ", timezone.now())
            #procesamos cada linea
            linea = linea.split(',')
            if linea[0]:
                domicilio = Domicilio()
                domicilio.individuo = individuos[linea[0]]
                domicilio.localidad = localidades[linea[4]]
                domicilio.calle = linea[3]
                domicilio.aclaracion = "PADRON"
                domicilios.append(domicilio)
        
        #Mandamos respuesta
        print("Fin del proceso de carga!")