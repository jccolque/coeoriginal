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
#Imports de la app
from consultas.choices import TIPO_TELEFONISTA
from consultas.models import Telefonista

def crear_telefonistas(filename):
    #obtenemos el comite de vigilancia Epidemiologica
    subcomite = SubComite.objects.get_or_create(nombre="MINISTERIO DE CULTURA Y TURISMO")[0]
    tipos= [tipo[0] for tipo in TIPO_TELEFONISTA]
    #Procesamos el archivo
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            print("\nProcesamos " + row[0] + ': ' + row[1] + ', ' + row[2])
            #Procesamos linea: 0-DNI 1-Apellido 2-Nombre 3-E-mail 4-Teléfono 5-max_pendientes 6-Tipo
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
            new_operador.usuario.user_permissions.add(permisos.get(codename='menu_informacion'))
            new_operador.usuario.user_permissions.add(permisos.get(codename='individuos'))
            new_operador.usuario.user_permissions.add(permisos.get(codename='telefonistas'))
            #Creamos vigilante
            if not Telefonista.objects.filter(operador=new_operador).exists():
                if row[6] in tipos:
                    telefonista = Telefonista()
                    telefonista.tipo = row[6]
                    telefonista.operador = new_operador
                    telefonista.max_controlados = row[5]
                    telefonista.save()
                    print("Creamos telefonista")
                elif row[6] == 'ADM_TEL':
                    new_operador.usuario.user_permissions.add(permisos.get(codename='admin_telefonistas'))
                    new_operador.usuario.user_permissions.add(permisos.get(codename='menu_operadores'))
                    new_operador.usuario.user_permissions.add(permisos.get(codename='administrador'))
                    print("Creamos Administrador de Call Center.")
            else:
                print("Ya es telefonista. No Procesado")