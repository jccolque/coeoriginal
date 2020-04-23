#Imports de python
import csv
#Imports del proyecto
from informacion.models import Individuo
from inscripciones.models import Inscripto
from georef.functions import obtener_argentina

def reasginar_inscriptos(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            #Estructura: 0-num_doc	1-nombres	2-apellidos	3-telefono	4-email	5-id_registro
            print('Procesamos a: ' + row[1] + ' ' +row[2])
            try:
                #Buscamos y actualizmaos individuo
                individuo = Individuo.objects.get(num_doc=row[0])
                inscripto = Inscripto.objects.get(pk=row[5], individuo=None)
            except Individuo.DoesNotExist:
                #No existe el individuo, lo creamos
                individuo = Individuo()
                individuo.num_doc = row[0]
                individuo.apellidos = row[2]
                individuo.nombres = row[1]
                individuo.nacionalidad = obtener_argentina
                print("No existia el individuo, lo creamos.")
            except Inscripto.DoesNotExist:
                print("Ya fue asignado, no hace falta.")    
            #Terminado el proceso de sanitizacion de invidiuo:
            individuo.telefono = row[3]
            individuo.email = row[4]
            individuo.save()
            #Asignamos individuo
            inscripto.individuo = individuo
            inscripto.save()
            print("Salvamos registro")