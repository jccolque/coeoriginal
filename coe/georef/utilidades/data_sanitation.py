#Imports de python
import csv
#Imports del proyecto
from informacion.models import Domicilio#localidad
from informacion.models import Individuo#destino
#Imports de la app
from georef.models import Provincia, Localidad

def cargar_ids_infra_provincias(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            print("\nProcesamos " + row[0] + ': ' + row[1] + ', ' + row[2])
            p = Provincia.objects.get(id=row[1])
            p.id_infragob = row[2]
            p.save()

def cargar_ids_infra_localidades(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            print("\nProcesamos " + row[0] + ': ' + row[1] + ', ' + row[2])
            l = Localidad.objects.get(id=row[1])
            l.id_infragob = row[2]
            l.save()
