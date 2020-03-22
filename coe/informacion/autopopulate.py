#Imports django
from django.utils import timezone
from georef.models import Nacionalidad, Departamento, Localidad
#Imports de la app
from .models import Individuo, Domicilio

def upload_padron(request):
    print("Carga Masiva de Padron: ", timezone.now())
    with open("PADRON_BASIC.csv", encoding="utf8") as lines:
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
        for linea in lines:
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
        print("Guardando: ", timezone.now())
        #Guardamos y generamos ids
        Individuo.objects.bulk_create(individuos)
        print("Cantidad de Individuos Procesados:", len(individuos))
        #Indexamos id:individuos en un dict
        individuos = {i.num_doc: i for i in Individuo.objects.all()}
        #Cargamos domicilios
        print("Comenzamos a cargar Domicilios", timezone.now())
        domicilios = []
        for linea in lines:#Agregamos los domicilios
            linea = linea.split(',')
            if linea[0]:
                domicilio = Domicilio()
                domicilio.individuo = individuos[linea[0]]
                domicilio.localidad = localidades[linea[4]]
                domicilio.calle = linea[3]
                domicilio.aclaracion = "PADRON"
                domicilios.append(domicilio)
        print("Guardando: ", timezone.now())
        Domicilio.objects.bulk_create(domicilios)
        #Mandamos respuesta
        print("Fin del proceso de carga!")