#Imports de python
import csv
from datetime import datetime
#Imports de Django
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
#Imports del proyecto
from coe.constantes import NOTEL
from informacion.models import Individuo
from operadores.models import SubComite, Operador
from operadores.functions import crear_usuario
from inscripciones.models import Inscripcion
#Imports de la app
from seguimiento.choices import TIPO_VIGIA
from seguimiento.models import Seguimiento, Vigia
from seguimiento.functions import realizar_alta_seguimiento, obtener_bajo_seguimiento

def crear_vigias(filename):
    #obtenemos el comite de vigilancia Epidemiologica
    subcomite = SubComite.objects.get_or_create(nombre="Vigilancia Epidemiologica")[0]
    tipos_vigia = [tipo[0] for tipo in TIPO_VIGIA]
    #Procesamos el archivo
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            print("\nProcesamos " + row[0] + ': ' + row[1] + ', ' + row[2])
            #Procesamos linea: 0-DNI 1-Apellido 2-Nombre 3-E-mail 4-Teléfono 5-max_controlados 6-Tipo 7-Origen
            #OPERADOR:
            if not Operador.objects.filter(num_doc=row[0]).exists():
                print("Operador Creado")
                #Creamos Operador
                new_operador = Operador()
                new_operador.subcomite = subcomite
                new_operador.num_doc = row[0]
                new_operador.apellidos = row[1]
                new_operador.nombres  = row[2]
                new_operador.email = row[3]
                new_operador.telefono = row[4]
                new_operador.save()
            else:
                print("Ya existe Operador")
                new_operador = Operador.objects.get(num_doc=row[0])
            #USUARIO
            if not new_operador.usuario:
                #Creamos usuario:
                new_operador.usuario = crear_usuario(new_operador)
                new_operador.save()
                print("Creamos usuario: " + new_operador.usuario.username)
            else:
                print("Ya Tenia usuario: " + new_operador.usuario.username)
            
            #Otorgamos permisos:
            #Obtenemos todos los permisos Custom:
            permisos = Permission.objects.filter(content_type__app_label='operadores', content_type__model='operador')
            #Agregamos permisos Basicos
            new_operador.usuario.user_permissions.add(permisos.get(codename='individuos'))
            new_operador.usuario.user_permissions.add(permisos.get(codename='seguimiento'))
            #Creamos vigilante
            if row[6] in tipos_vigia:
                #Chequeamos que no sea vigilante:
                if Vigia.objects.filter(operador=new_operador).exists():
                    Vigia.objects.filter(operador=new_operador).update(tipo=row[6], max_controlados=row[5])
                    print("Actualizamos vigilante (Le van a quedar asignados los controlados")
                else:
                    vigia = Vigia(operador=new_operador)
                    vigia.tipo = row[6]
                    vigia.max_controlados = row[5]
                    vigia.save()
                    print("Creamos Vigia")
            elif row[6] == 'CARGA':
                    new_operador.usuario.user_permissions.add(permisos.get(codename='epidemiologia'))
                    print("Creamos Cargador.")
            elif row[6] == 'ADM_SEG':
                new_operador.usuario.user_permissions.add(permisos.get(codename='seguimiento_admin'))
                new_operador.usuario.user_permissions.add(permisos.get(codename='operadores'))#Puede crear usuarios
                new_operador.usuario.user_permissions.add(permisos.get(codename='administrador'))#Puede crear usuarios
                print("Creamos Administrador de Seguimiento.")

def altas_masivas(filename):
    #Procesamos el archivo
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            try:
                individuo = Individuo.objects.get(num_doc=row[0])
                realizar_alta_seguimiento(individuo, 'Archivo CSV Masivo')
                print("Alta generada para:" + str(individuo))
            except Individuo.DoesNotExist:
                print("No existe DNI: " + row[0])

def marcar_sin_telefono():
    print("Iniciamos marcado de falta de telefonos")
    individuos = obtener_bajo_seguimiento()
    individuos = individuos.filter(telefono=NOTEL)
    seguimientos = []
    for individuo in individuos:
        print(individuo)
        seg = Seguimiento(individuo=individuo)
        seg.tipo = 'TE'
        seg.aclaracion = 'Analisis Inicial'
        seguimientos.append(seg)
    #Lanzamos guardado masivo
    Seguimiento.objects.bulk_create(seguimientos)

def obtener_last_seg():
    print("Iniciamos carga de seguimientos actuales")
    individuos = obtener_bajo_seguimiento()
    individuos = individuos.filter(seguimiento_actual=None)
    print("Debemos procesar: " + str(individuos.count()) + "registros.")
    for individuo in individuos:
        individuo.seguimiento_actual = individuo.seguimientos.last()
        individuo.save()
        print(individuo)

def confirmar_individuos(filename):
    from georef.models import Localidad
    from georef.functions import obtener_argentina
    from informacion.models import Atributo
    #Cargamos masivamente los test positivos:
    with open(filename) as csv_file:
        argentina = obtener_argentina()
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            print(row)
            #0-DNI	1-FECHA	2-Apellido	3-Nombres	4-LOCALIDAD	5-DOMICILIO	6-BARRIOS	7-SEXO	8-EDAD	9-TELEFONO
            try:
                individuo = Individuo.objects.get(num_doc=row[0])
                if individuo.get_situacion().conducta == 50:
                    print("Ya se encuentra confirmado")
                    continue
                print("Existe: " + str(individuo))
            except:
                individuo = Individuo(num_doc=row[0])
                individuo.apellidos = row[2]
                individuo.nombres = row[3]
                individuo.sexo = row[7]
                individuo.telefono = row[9]
                individuo.nacionalidad = argentina
                individuo.save()
                print("Creamos: " + str(individuo))
                #Creamos domicilio
            #Tenemos el individuo:
            if row[8] and int(row[8]) > 64:
                atrib = Atributo(individuo=individuo)
                atrib.tipo = "PR"
                atrib.aclaracion = "Mayor de 65 años."
                atrib.save()
                print("Marcado como Poblacion de Riesgo")
            #Le cargamos el seguimiento de confirmado por test:
            seguimiento = Seguimiento(individuo=individuo)
            seguimiento.tipo = "CT"
            seguimiento.fecha = datetime.strptime(row[1], "%d/%m/%Y").date()
            seguimiento.aclaracion = "Obtenido de Excel de Epidemiologia"
            seguimiento.save()
            print("Marcado como confirmado.")

def subir_viejitos(filename):
    #Imports requeridos
    from georef.models import Localidad
    from georef.functions import obtener_argentina
    from informacion.models import Individuo, Domicilio
    from informacion.models import Atributo
    #Generamos datos basicos:
    argentina = obtener_argentina()
    dict_localidades = {l.id_infragob:l for l in Localidad.objects.filter(departamento__provincia__id_infragob=38)}
    dict_vigilados = set(a.individuo.id for a in Atributo.objects.filter(tipo='VD'))
    #Leemos el archivo csv
    with open(filename, encoding='ISO-8859-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            #0-nrodoc	1-apellido	2-nombre	3-fecnac	4-sexo	5-calle	6-NroPta	7-barrio	8-localidad_id	9-telefonos
            #Obtenemos individuo:
            try:
                individuo = Individuo.objects.get(num_doc=row[0])
            except:
                individuo = Individuo(num_doc=row[0])
            #Cargamos la informacion:
            individuo.apellidos = row[1]
            individuo.nombres = row[2]
            try:
                individuo.fecha_nacimiento = datetime.strptime(row[3], "%Y-%m-%d").date()
            except:
                try:
                    individuo.fecha_nacimiento = datetime.strptime(row[3], "%d/%m/%Y").date()
                except:
                    pass
            individuo.sexo = row[4]
            individuo.nacionalidad = argentina
            individuo.telefono = row[9]
            #Limpiamos / (inicio y final)
            try:
                if individuo.telefono[0] == "/":
                    individuo.telefono = individuo.telefono[1:]
                if individuo.telefono[-1] == "/":
                    individuo.telefono = individuo.telefono[:-1]
            except:
                pass
            individuo.save()#Guardamos
            #Generamos domicilio
            if row[5]:
                domicilio = Domicilio(individuo=individuo)
                domicilio.localidad = dict_localidades[row[8]]
                domicilio.calle = row[5]
                domicilio.numero = row[6]
                domicilio.aclaracion = row[7]
                domicilio.save()
            #Atributo a generar: ('VD', 'Vigilancia de Adultos Mayores'),
            if individuo.id not in dict_vigilados:
                atributo = Atributo(individuo=individuo)
                atributo.tipo = "VD"
                atributo.aclaracion = "Se cargo masivamente de archivo."
                atributo.save()
                print(str(individuo) + " Puesto bajo Vigilancia.")
            else:
                print(str(individuo) + " Ya estaba bajo vigilancia.")

def cargar_matricula(filename):
    #Imports requeridos
    from georef.functions import obtener_argentina
    from informacion.models import Individuo, Atributo
    from operadores.models import Operador
    #Generamos datos basicos:
    argentina = obtener_argentina()
    #Leemos el archivo csv
    with open(filename, encoding='ISO-8859-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            #0-nrodoc	1-apellido	2-nombre	3-matricula	4-aclaracion_vigia
            #Obtenemos operador:
            try:
                operador = Operador.objects.get(num_doc=row[0])
                try:#Actualizamos aclaracion de Vigia
                    vigia = operador.vigia
                    vigia.aclaracion = row[4]
                    vigia.save()
                except:
                    print(str(operador) + ' No es vigia.')
                #Obtenemos individuo:
                try:
                    individuo = Individuo.objects.get(num_doc=row[0])
                except:#Si no existe lo creamos super basico
                    individuo = Individuo(num_doc=row[0])
                    individuo.apellidos = row[1]
                    individuo.nombres = row[2]
                    individuo.nacionalidad = argentina
                    individuo.save()#Guardamos
                #Generamos Atributo de matricula
                atributo = Atributo(individuo=individuo)
                atributo.tipo = "PM"
                atributo.aclaracion = row[3]
                atributo.save()
                print('Matricula cargada para: ' + str(individuo))
            except:
                print(row[0] +': ' + row[1] + " No es operador del sistema.")
