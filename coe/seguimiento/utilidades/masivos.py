#Imports de python
import csv
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
from seguimiento.models import Seguimiento, Vigia
from seguimiento.functions import realizar_alta, obtener_bajo_seguimiento

def crear_vigias(filename):
    #obtenemos el comite de vigilancia Epidemiologica
    subcomite = SubComite.objects.get_or_create(nombre="Vigilancia Epidemiologica")[0]
    #Procesamos el archivo
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            print("\nProcesamos " + row[0] + ': ' + row[1] + ', ' + row[2])
            #Procesamos linea: 0-DNI 1-Apellido 2-Nombre 3-E-mail 4-Teléfono 5-max_controlados 6-Tipo
            #OPERADOR:
            if not Operador.objects.filter(num_doc=row[0]).exists():
                print("Creamos Operador")
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
            #Otorgamos Solo permisos para vigilancia:
            permisos = Permission.objects.filter(content_type__app_label='operadores', content_type__model='operador')
            new_operador.usuario.user_permissions.add(permisos.get(codename='individuos'))
            new_operador.usuario.user_permissions.add(permisos.get(codename='seguimiento'))
            #Creamos vigilante
            if not Vigia.objects.filter(operador=new_operador).exists():
                if row[6] in ('VE', 'VM', 'ST', 'VT'):
                    vigia = Vigia()
                    vigia.tipo = row[6]
                    vigia.operador = new_operador
                    vigia.max_controlados = row[5]
                    vigia.save()
                    print("Creamos Vigia")
                elif row[6] == 'A':
                    new_operador.usuario.user_permissions.add(permisos.get(codename='seguimiento_admin'))
                    print("Creamos Administrador de Seguimiento.")
            else:
                print("Ya es vigia.")

def altas_masivas(filename):
    #Procesamos el archivo
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            try:
                individuo = Individuo.objects.get(num_doc=row[0])
                realizar_alta(individuo, 'Archivo CSV Masivo')
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
    #Cargamos masivamente los test positivos:
     with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            pass