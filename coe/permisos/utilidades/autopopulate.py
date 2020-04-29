#Imports de Python
from datetime import time
#Imports del proyecto
from permisos.choices import TIPO_PERMISO
from permisos.models import NivelRestriccion

#Funciones de inicializacion
def crear_niveles_basicos():
    NivelRestriccion.objects.all().delete()
    #for tipo in TIPO_PERMISO:
    #    nivel.tramites_admitidos.append(tipo[0])
    #Nivel Verde
    nivel = NivelRestriccion()
    nivel.color = 'V'
    nivel.inicio_horario = time(8,0)
    nivel.cierre_horario = time(20,0)
    nivel.poblacion_maxima = 75
    nivel.duracion_permiso = 4
    #for tipo in TIPO_PERMISO:
    #    nivel.tramites_admitidos.append(tipo[0])
    nivel.save()
    #Nivel Amarillo
    nivel = NivelRestriccion()
    nivel.color = 'A'
    nivel.inicio_horario = time(8,0)
    nivel.cierre_horario = time(17,0)
    nivel.poblacion_maxima = 50
    nivel.duracion_permiso = 2
    #for tipo in TIPO_PERMISO:
    #    nivel.tramites_admitidos.append(tipo[0])
    nivel.save()
    #Nivel Rojo
    nivel = NivelRestriccion()
    nivel.color = 'R'
    nivel.inicio_horario = time(8,0)
    nivel.cierre_horario = time(14,0)
    nivel.poblacion_maxima = 25
    nivel.duracion_permiso = 1
    #for tipo in TIPO_PERMISO:
    #    nivel.tramites_admitidos.append(tipo[0])
    nivel.save()
    #Nivel Negro
    nivel = NivelRestriccion()
    nivel.color = 'D'
    nivel.inicio_horario = time(0,0)
    nivel.cierre_horario = time(0,0)
    nivel.poblacion_maxima = 0
    nivel.duracion_permiso = 0
    #for tipo in TIPO_PERMISO:
    #    nivel.tramites_admitidos.append(tipo[0])
    nivel.save()