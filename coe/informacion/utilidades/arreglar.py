#Imports de Python
from datetime import datetime, time
#Imports de Django
from django.utils import timezone
#Imports del proyecto
from informacion.models import Individuo

def arreglar_horario_ingreso():
    individuos = Individuo.objects.exclude(domicilio_actual__ubicacion=None)
    for individuo in individuos:
        print("Acomodamos Horario para " + str(individuo))
        dom = individuo.domicilio_actual
        dom.fecha = datetime.combine(dom.fecha.date(), time(6,0))#Horario Fijo
        dom.save()