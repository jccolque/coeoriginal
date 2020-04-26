#Imports de Python
from datetime import time
#Imports del proyecto
from permisos.choices import TIPO_PERMISO
from permisos.models import NivelRestriccion

#Funciones de inicializacion
def crear_niveles_basicos():
    NivelRestriccion.objects.all().delete()
    #Nivel Blanco
    nivel = NivelRestriccion()
    nivel.color = 'B'
    nivel.inicio_horario = time(0,0)
    nivel.cierre_horario = time(23,59)
    nivel.poblacion_maxima = 100
    nivel.grupos_permitidos = 1
    nivel.duracion_permiso = 24
    #for tipo in TIPO_PERMISO:
    #    nivel.tramites_admitidos.append(tipo[0])
    nivel.save()
    #Nivel Verde
    nivel = NivelRestriccion()
    nivel.color = 'V'
    nivel.inicio_horario = time(8,0)
    nivel.cierre_horario = time(20,0)
    nivel.poblacion_maxima = 75
    nivel.grupos_permitidos = 2
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
    nivel.grupos_permitidos = 3
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
    nivel.grupos_permitidos = 5
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
    nivel.grupos_permitidos = 0
    nivel.duracion_permiso = 0
    #for tipo in TIPO_PERMISO:
    #    nivel.tramites_admitidos.append(tipo[0])
    nivel.save()