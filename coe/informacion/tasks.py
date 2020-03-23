#Traemos el sistema de Backgrounds

#Imports de Python
from dateutil.relativedelta import relativedelta
from background_task import background
#Imports django
from django.utils import timezone
from django.db.models import Q
#Imports del proyecto
from georef.models import Nacionalidad, Departamento, Localidad
#Import Personales
from .models import Archivo
from .models import Individuo, Domicilio
from .models import Seguimiento
from .models import TipoSintoma, TipoAtributo
from .models import Sintoma, Atributo
from .choices import TIPO_SINTOMA

@background(schedule=1)
def guardar_same(lineas, archivo_id):
    archivo = Archivo.objects.get(pk=archivo_id)
    if not archivo.descripcion:
        archivo.descripcion = "<h3>Inicia la carga Background: "+str(timezone.now())+"</h3>"
        archivo.save()
    #Contadores
    cant_subidos = 0
    cant_fallos = 0
    #Obtenemos datos necesarios
    nac = Nacionalidad.objects.get_or_create(nombre="Argentina")[0]
    #Procesamos todas las lineas
    for linea in lineas:
        #0Fecha	1Hora	2Paciente	3Síntomas	4Edad	5DNI	6Domicilio	7Telefono	8Desenlace	9Motivo	10Observaciones
        linea = linea.split(';')#La spliteamos
        if linea[0] and linea[5]:
            linea[5] = linea[5].replace('.','')
            try:#Si lo encontramos ya tenemos todos los datos basicos
                individuo = Individuo.objects.get(num_doc=linea[5])
            except Individuo.DoesNotExist:#Si no lo agregamos
                individuo = Individuo()
                individuo.num_doc = linea[5]
                individuo.nombres = linea[2]
                individuo.apellidos = "SAME-CORREGIR"
                individuo.nacionalidad = nac
            #Agregamos Datos utiles:   
            if not individuo.fecha_nacimiento:
                individuo.fecha_nacimiento = timezone.now().date() - relativedelta(years=int(linea[4]))
            if not individuo.telefono:
                individuo.telefono = linea[7]
            individuo.observaciones = "<p>"+linea[10]+"</p><p>Domicilio: "+linea[6]+"</p><p>Desenlace:"+linea[8]+"</p>"
            individuo.save()
            cant_subidos += 1
            archivo.descripcion += "<li>"+str(individuo)+"</li>"
            archivo.save()
            #Cargamos seguimiento> Llamado al same
            seguimiento = Seguimiento()
            seguimiento.individuo = individuo
            seguimiento.aclaracion = "CARGA SAME"
            d = linea[0].split('/')
            h = linea[1].split(':')
            seguimiento.fecha = timezone.datetime(int(d[2]),int(d[0]),int(d[1]), int(h[0]), int(h[1]))
            seguimiento.save()
            #Intentamos procesar sintomas:
            for tsintoma in TIPO_SINTOMA:
                if tsintoma[0] in linea[3].upper():
                    sintoma = Sintoma()
                    sintoma.individuo = individuo
                    sintoma.tipo = TipoSintoma.objects.first()
                    sintoma.newtipo = tsintoma[0]
                    sintoma.aclaracion = "SAME: "+linea[3]
                    sintoma.save()
            #Poblacion de riesgo:
            riesgos = ['HTA', 'DBT', 'EMBAR', 'INMUN', 'ASMA', 'BRONQ', 'CARDIA', 'RENAL']
            for riesgo in riesgos:
                if riesgo in linea[3].upper():
                    atributo = Atributo()
                    atributo.individuo = individuo
                    atributo.tipo = TipoAtributo.objects.get(
                        Q(nombre__icontains='poblacion') & 
                        Q(nombre__icontains='riesgo')
                    )
                    atributo.newtipo = 'PR'
                    atributo.aclaracion = "SAME: "+linea[3]
                    atributo.save()
        else:
            cant_fallos += 1
            archivo.descripcion += "<li><b>No se Proceso:</b>"+str(linea[0:4])+"...</li>"
            archivo.save()
    #Resultado final
    archivo.descripcion += "</ul>"
    archivo.descripcion += "<p>FIN DEL PROCESAMIENTO</p>"
    archivo.descripcion += "<p>Subidos: "+str(cant_subidos)+"</p>"
    archivo.descripcion += "<p>Fallidos: "+str(cant_fallos)+"</p>"
    archivo.procesado = True
    archivo.save()

@background(schedule=1)
def guardar_padron_individuos(lineas, archivo_id):
    archivo = Archivo.objects.get(pk=archivo_id)
    if not archivo.descripcion:
        archivo.descripcion = "<h3>Inicia la carga Masiva del Padron: "+str(timezone.now())+"</h3>"
        #Limpiamos la base de datos:
        archivo.descripcion += "<li> Eliminamos cargados de ultimo Padron: "+ str(timezone.now())
        Individuo.objects.filter(observaciones="PADRON").delete()
        archivo.save()
    #Obtenemos dni existentes
    num_docs_existentes = [i.num_doc for i in Individuo.objects.all()]
    #Generamos elementos basicos:
    nac = Nacionalidad.objects.get_or_create(nombre="Argentina")[0]
    #GEneramos todos los elementos nuevos
    individuos = []
    archivo.descripcion += "<li> Inicio de Procesamiento: "+ str(timezone.now())
    archivo.descripcion += "<p>Cantidad Lineas: "+str(len(lineas))+"</p>"
    for linea in lineas:
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
            #Lo agregamos a la lista
            if individuo.num_doc not in num_docs_existentes:
                num_docs_existentes.append(individuo.num_doc)
                individuos.append(individuo)    
    #Creamos este bloque
    Individuo.objects.bulk_create(individuos)
    archivo.descripcion += "<li>Guardando Fragmento: "+ str(timezone.now())
    archivo.save()
        
@background(schedule=1)
def guardar_padron_domicilios(lineas, archivo_id):
    archivo = Archivo.objects.get(pk=archivo_id)
    if not archivo.descripcion:
        archivo.descripcion = "<h3>Inicia la carga Masiva de Domicilios del Padron: "+str(timezone.now())+"</h3>"
        #Limpiamos la base de datos:
        archivo.descripcion += "<li> Eliminamos cargados de ultimo Padron: "+ str(timezone.now())
        archivo.save()
    #Agregamos info al doc
    archivo.descripcion += "<p>Cantidad Lineas: "+str(len(lineas))+"</p>"    
    #Generamos listado de individuos para matchear
    individuos = {i.num_doc: i for i in Individuo.objects.all()}
    #Generamos lista de localidades para matchear
    localidades = {l.nombre: l for l in Localidad.objects.all()}
    #Cargamos domicilios
    domicilios = []
    for linea in lineas:#Agregamos los domicilios
        linea = linea.split(',')
        if linea[0]:
            #Si no existe la localidad la creamos
            if linea[2] not in localidades:
                log+= "<li> Se creo: ", linea[4]+ str('| Hay que Corregir el Departamento.')
                localidad = Localidad()
                localidad.departamento = Departamento.objects.first()
                localidad.nombre = linea[4]
                localidad.save()
                localidades[localidad.nombre] = localidad
            #Si existe el individuo en nuestra base de datos
            if linea[0] in individuos:
                domicilio = Domicilio()
                domicilio.individuo = individuos[linea[0]]
                domicilio.localidad = localidades[linea[2]]
                domicilio.calle = linea[1]
                domicilio.aclaracion = "PADRON"
                domicilios.append(domicilio)
    #Creamos este bloque
    Domicilio.objects.bulk_create(domicilios)
    archivo.descripcion += "<li>Guardando Fragmento Domicilios: "+ str(timezone.now())
    archivo.save()
            