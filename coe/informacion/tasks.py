#Traemos el sistema de Backgrounds

#Imports de Python
import logging
import traceback
from datetime import timedelta
#Imports django
from django.utils import timezone
from dateutil.relativedelta import relativedelta
#Imports extras
from background_task import background
#Imports del proyecto
from coe.constantes import DIAS_CUARENTENA
from georef.models import Nacionalidad, Departamento, Localidad
#Import Personales
from .models import Archivo
from .models import Individuo, Domicilio
from .models import Seguimiento
from .models import Situacion, Sintoma, Atributo

#Definimos logger
logger = logging.getLogger("tasks")

#Reconocedores
Rsintomas = [
    ('DPR', 'Respirar'),
    ('DM', 'Muscular'),
    ('DRO', 'Ocular'),
    ('ART', 'Articul'),
    ('DC', 'Cabeza'),
    ('DC', 'Cefalea'),
    ('DG', 'Garganta'),
    ('DP', 'Pecho'),
    ('DSV', 'Vientre'),
    ('FAT', 'Fatiga'),
    ('FIE', 'Fiebre'),
    ('HEP', 'Hemorragia'),
    ('MAR', 'Mareos'),
    ('NAS', 'Nauseas'),
    ('PAL', 'Palidez'),
    ('PDA', 'Apetito'),
    ('RCA', 'Cardiaco'),
    ('RCA', 'Taquicard'),
    ('SAR', 'Sarpulli'),
    ('SN', 'Nasal'),
    ('TOS', 'Tos'),
    ('VOM', 'Vomit'),
    ('ESC', 'Escalof')
]
Rriesgos = ['HIPER', 'TENSION', 'DBT', 'DIABE', 'EMBARA', 'INMUN', 'ASMA', 'BRONQ', 'CARDIA', 'CARDIO', 'RENAL']

@background(schedule=1)
def guardar_same(lineas, archivo_id, ultimo=False):
    logger.info("Iniciamos Carga Same")
    archivo = Archivo.objects.get(pk=archivo_id)
    if not archivo.descripcion:
        archivo.descripcion = "<h3>Inicia la carga Background SAME: "+str(timezone.now())+"</h3>"
    #Contadores
    cant_subidos = 0
    cant_fallos = 0
    #Obtenemos datos necesarios
    nac = Nacionalidad.objects.filter(nombre__icontains="Argentina").first()
    #Procesamos todas las lineas
    archivo.descripcion += "<p>INICIO BLOQUE</p><ul>"
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
            #Cargamos Situacion
            situacion = Situacion()
            situacion.individuo = individuo
            situacion.estado = 11
            situacion.conducta = 'B'
            situacion.aclaracion = "CARGA SAME"
            situacion.save()
            #Cargamos seguimiento> Llamado al same
            seguimiento = Seguimiento()
            seguimiento.individuo = individuo
            seguimiento.aclaracion = "CARGA SAME"
            d = linea[0].split('/')
            h = linea[1].split(':')
            seguimiento.fecha = timezone.datetime(int(d[2]),int(d[1]),int(d[0]), int(h[0]), int(h[1]))
            seguimiento.save()
            #Intentamos procesar sintomas:
            for sintoma in Rsintomas:
                if sintoma[1].upper() in linea[3].upper():
                    sintoma = Sintoma()
                    sintoma.individuo = individuo
                    sintoma.tipo = sintoma[0]
                    sintoma.aclaracion = "CARGA SAME: "+linea[3][0:190]
                    sintoma.save()
            #Poblacion de riesgo:
            for riesgo in Rriesgos:
                if riesgo in linea[3].upper():
                    atributo = Atributo()
                    atributo.individuo = individuo
                    atributo.tipo = 'PR'
                    atributo.aclaracion = "CARGA SAME: "+linea[3][0:190]
                    atributo.save()
            #Lista la linea
            cant_subidos += 1
            archivo.descripcion += "<li>"+str(individuo)+"</li>"
        else:
            cant_fallos += 1
            archivo.descripcion += "<li><b>No se Proceso:</b>"+str(linea[0:4])+"...</li>"
    #Resultado final
    archivo.descripcion += "</ul>"
    archivo.descripcion += "<p>Subidos: "+str(cant_subidos)+"- Fallidos: "+str(cant_fallos)+"</p></p>"
    archivo.descripcion += "<p>FIN BLOQUE</p>"
    archivo.save()
    if ultimo:
        archivo.descripcion += "<p>FIN ARCHIVO</p>"
        archivo.procesado = True
        archivo.save()
    logger.info("Finalizamos Carga Same\n")

@background(schedule=1)
def guardar_epidemiologia(lineas, archivo_id, ultimo=False):
    logger.info("Iniciamos Carga de Epidemiologia")
    archivo = Archivo.objects.get(pk=archivo_id)
    if not archivo.descripcion:
        archivo.descripcion = "<h3>Inicia la carga Background Epidemiologia: "+str(timezone.now())+"</h3>"
    #Contadores
    cant_subidos = 0
    cant_fallos = 0
    #Obtenemos datos necesarios
    nac = Nacionalidad.objects.filter(nombre__icontains="Argentina").first()
    san_salvador = Localidad.objects.filter(nombre__icontains="SAN SALVADOR").first()
    #Procesamos todas las lineas
    archivo.descripcion += "<p>INICIO BLOQUE</p><ul>"
    for linea in lineas:
        linea = linea.split(';')#La spliteamos
        #0DNI	1APELLIDO	2NOMBRE
        if linea[0]:
            linea[0] = linea[0].replace('.','')
            try:#Si lo encontramos ya tenemos todos los datos basicos
                individuo = Individuo.objects.get(num_doc=linea[0])
            except Individuo.DoesNotExist:#Si no lo agregamos
                individuo = Individuo()
                individuo.num_doc = linea[0]
                individuo.apellidos = linea[1]
                individuo.nombres = linea[2]
                individuo.nacionalidad = nac
            #Cargamos telefono
            if linea[6]:
                individuo.telefono = linea[6]
            #Agregamos Datos utiles:   
            if not individuo.fecha_nacimiento:
                individuo.fecha_nacimiento = timezone.now().date()
            individuo.observaciones = "<p> Cargado desde Excel de Epidemiologia</p>"
            if linea[7]:#Viajo A
                individuo.observaciones += "<p> Viajo a: "+linea[6]+"</p>" 
            #Listo el individuo
            individuo.save()
            #Agregamos domicilio si no lo tiene:
            #3CODIGOPOSTAL	4DOMICILIO 5NUMERO	6CELULAR
            if linea[4]:
                domicilio = Domicilio()
                domicilio.individuo = individuo
                domicilio.calle = linea[4]
                if linea[5]:
                    domicilio.numero = linea[5]
                else:
                    domicilio.numero = 'EPIDEMIOLOGIA:CORREGIR'
                #Le metemos localidad
                if linea[3]:
                    domicilio.localidad = Localidad.objects.filter(codigo_postal=linea[3]).first()
                if not hasattr(domicilio, 'localidad'):
                    domicilio.localidad = san_salvador
                domicilio.aclaracion = "EPIDEMIOLOGIA"
                domicilio.save()
            #Cargamos seguimiento> Llamado al same
            seguimiento = Seguimiento()
            seguimiento.individuo = individuo
            seguimiento.aclaracion = "EPIDEMIOLOGIA"
            seguimiento.save()
            #Cargamos Situacion
            situacion = Situacion()
            situacion.individuo = individuo
            situacion.estado = 11
            situacion.conducta = 'C'
            situacion.aclaracion = "EPIDEMIOLOGIA"
            situacion.save()
            # DIA 1 a 14 (del 8 al 21)
            #No Intentamos procesar sintomas pues mete mucha basura:
            for dia in linea[7:]:
                if dia:
                    seguimiento = Seguimiento()
                    seguimiento.individuo = individuo
                    seguimiento.aclaracion = "EPIDEMIOLOGIA" + dia[0:190]
                    seguimiento.save()
                    #Intentamos identificar sintomas
                    for sintoma in Rsintomas:
                        if sintoma[1].upper() in linea[3].upper():
                            sintoma = Sintoma()
                            sintoma.individuo = individuo
                            sintoma.tipo = sintoma[0]
                            sintoma.aclaracion = "EPIDEMIOLOGIA: " + linea[3][0:190]
                            sintoma.save()
            #Lista la linea
            cant_subidos += 1
            archivo.descripcion += "<li>"+str(individuo)+"</li>"
        else:
            cant_fallos += 1
            archivo.descripcion += "<li><b>No se Proceso:</b>"+str(linea[0:4])+"...</li>"
    #Resultado final
    archivo.descripcion += "</ul>"
    archivo.descripcion += "<p>Subidos: "+str(cant_subidos)+"- Fallidos: "+str(cant_fallos)+"</p>"
    archivo.descripcion += "<p>FIN BLOQUE</p>"
    archivo.save()
    if ultimo:
        archivo.descripcion += "<p>FIN ARCHIVO</p>"
        archivo.procesado = True
        archivo.save()
    logger.info("Finalizamos Carga Epidemiologia\n")

@background(schedule=1)
def guardar_padron_individuos(lineas, archivo_id, ultimo=False):
    logger.info("Iniciamos carga del Padron")
    archivo = Archivo.objects.get(pk=archivo_id)
    if not archivo.descripcion:
        archivo.descripcion = "<h3>Inicia la carga Masiva del Padron: "+str(timezone.now())+"</h3>"
        #Limpiamos la base de datos:
        archivo.descripcion += "<li> Eliminamos cargados de ultimo Padron: "+ str(timezone.now())
    #Obtenemos dni existentes
    num_docs_existentes = [i.num_doc for i in Individuo.objects.all()]
    #Generamos elementos basicos:
    nac = Nacionalidad.objects.filter(nombre__icontains="Argentina").first()
    #GEneramos todos los elementos nuevos
    individuos = []
    archivo.descripcion += "<li> Inicio de Procesamiento: "+ str(timezone.now())+"</li>"
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
    archivo.descripcion += "<li>Guardado Fragmento: "+ str(timezone.now())+"</li>"
    archivo.save()
    if ultimo:
        archivo.descripcion += "<p>FIN ARCHIVO</p>"
        archivo.procesado = True
        archivo.save()
    logger.info("Finalizamos carga del Padron\n")
        
@background(schedule=1)
def guardar_padron_domicilios(lineas, archivo_id, ultimo=False):
    logger.info("Iniciamos Carga del Padron")
    archivo = Archivo.objects.get(pk=archivo_id)
    if not archivo.descripcion:
        archivo.descripcion = "<h3>Inicia la carga Masiva de Domicilios del Padron: "+str(timezone.now())+"</h3>"
        #Limpiamos la base de datos:
        archivo.descripcion += "<li> Eliminamos cargados de ultimo Padron: "+ str(timezone.now())+"</li>"
    #Agregamos info al doc
    archivo.descripcion += "<p>Cantidad Lineas: "+str(len(lineas))+"</p>"    
    #Generamos listado de individuos para matchear
    individuos = {i.num_doc: i for i in Individuo.objects.all()}
    #Preparamos un depto para cuando se crea ciudad desconocida
    depto = Departamento.objects.first()
    #Generamos lista de localidades para matchear
    localidades = {l.nombre: l for l in Localidad.objects.all()}
    #Cargamos domicilios
    domicilios = []
    for linea in lineas:#Agregamos los domicilios
        linea = linea.split(',')
        if linea[0]:
            #Si no existe la localidad la creamos
            if linea[2] not in localidades:
                localidad = Localidad()
                localidad.departamento = depto
                localidad.nombre = linea[2]
                localidad.save()
                archivo.descripcion += "<li><b> Se creo: "+linea[2]+"| Hay que Corregirle el Departamento.</b></li>"
                localidades[localidad.nombre] = localidad
            #Si existe el individuo en nuestra base de datos
            if linea[0] in individuos:
                domicilio = Domicilio()
                domicilio.individuo = individuos[linea[0]]
                domicilio.localidad = localidades[linea[2]]
                domicilio.calle = linea[1]
                domicilio.aclaracion = "PADRON"
                domicilio.aislamiento = False
                domicilios.append(domicilio)
    #Creamos este bloque
    Domicilio.objects.bulk_create(domicilios)
    archivo.descripcion += "<li>Guardado Fragmento Domicilios: "+ str(timezone.now())
    archivo.save()
    if ultimo:
        archivo.descripcion += "<p>FIN ARCHIVO</p>"
        archivo.procesado = True
        archivo.save()
    logger.info("Finalizamos carga de Domicilio del Padron\n")

@background(schedule=1)
def baja_seguimiento():
    logger.info("Iniciamos Baja de Seguimiento")
    #Obtenemos fecha de corte:
    fecha_corte = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtenemos seguimientos iniciados antes de la fecha de corte
    seguimientos = Seguimiento.objects.filter(tipo='I', fecha__lt=fecha_corte)
    #Obtenemos todos los individuos seguidos
    individuos = Individuo.objects.filter(seguimientos__in=seguimientos).distinct()
    #Excluimos todos los ya dados de baja:
    individuos = individuos.exclude(seguimientos__tipo='FS')    
    #Los damos de baja
    for individuo in individuos:
        logger.info("Procesamos a: " + str(individuo))
        try:
            seguimiento = Seguimiento(individuo=individuo)
            seguimiento.tipo = 'FS'
            seguimiento.aclaracion = "Baja automatica por cumplir tiempo de cuarentena"
            seguimiento.save()
        except Exception as error:
            logger.info("Fallo baja_aislamiento: "+str(error)+'\n'+str(traceback.format_exc()))
    logger.info("Finalizamos Baja de Seguimiento\n")

@background(schedule=15)
def baja_aislamiento():
    logger.info("Iniciamos Baja de Aislamiento")
    #Obtenemos fecha de corte:
    fecha_corte = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtener aislados
    individuos = Individuo.objects.filter(situacion_actual__conducta='E')#Obtenemos a todos los aislados
    individuos = individuos.exclude(situacion_actual__fecha__gt=fecha_corte)#Evitamos a los que siguen en cuarentena
    #Damos de baja el aislamiento
    for individuo in individuos:
        logger.info("Procesamos a: " + str(individuo))
        try:
            #Lo sacamos de aislamiento
            situacion = Situacion(individuo=individuo)
            situacion.estado = 11
            situacion.conducta = 'C'
            situacion.aclaracion = "Baja por Cumplimiento de Cuarentena"
            situacion.save()  #  Guardamos
        except Exception as error:
            logger.info("Fallo baja_aislamiento: "+str(error)+'\n'+str(traceback.format_exc()))
    logger.info("Finalizamos Baja de Aislamiento\n")

@background(schedule=30)
def devolver_domicilio():
    logger.info("Iniciamos el Cambio de Domicilio")
    #Obtenemos fecha de corte:
    fecha_corte = timezone.now() - timedelta(days=DIAS_CUARENTENA)
    #Obtener aislados
    individuos = Individuo.objects.filter(domicilio_actual__aislado=True)
    individuos = individuos.exclude(domicilio_actual__ubicacion=None)#Quitamos los que no estan en hoteles
    #Les buscamos posible nuevo domicilio
    for individuo in individuos:
        logger.info("Procesamos a: " + str(individuo))
        try:
            dom = individuo.domicilios.filter(aislado=False).last()
            #Si tiene un domicilio valido que no es de aislamiento
            if not dom:
                dom = individuo.domicilio_actual
            #Lo blanqueamos para crearlo como nuevo:
            dom.pk = None
            dom.aislamiento = False
            dom.aclaracion = "Movido Automaticamente por final de Cuarentena."
            dom.fecha = None
            dom.save()
        except Exception as error:
            logger.info("Fallo Cambio de Domicilio: "+str(error)+'\n'+str(traceback.format_exc()))
    logger.info("Finalizamos devoluciones a Domicilios\n")
