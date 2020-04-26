#Imports de Python
from datetime import time, timedelta
#Imports de Django
from django.utils import timezone
from django.core.cache import cache
from django.http import JsonResponse
#Imports Extras
#Imports del proyecto
from coe.constantes import LAST_DATETIME, TIME_INICIO, TIME_FIN
#Imports de la app
from .models import NivelRestriccion, Permiso

#Funciones
def nivel_restriccion_actual():
    nivel_restriccion = cache.get("nivel_restriccion")
    if not nivel_restriccion:
        nivel_restriccion = NivelRestriccion.objects.get(activa=True)
        cache.set("nivel_restriccion", nivel_restriccion)
    return nivel_restriccion

#Salvoconducos
def buscar_permiso(individuo, activo=False):
    permisos = Permiso.objects.filter(individuo=individuo, endda__gt=timezone.now())
    permisos = permisos.select_related('individuo', 'individuo__domicilio_actual')
    if activo:#Si es control de Activo
        permisos = permisos.filter(begda__lt=timezone.now())
    #Obtenemos el mas cercano:
    permiso = permisos.first()
    if not permiso:
        #Si no tiene permiso generamos uno basico
        permiso = Permiso()
        permiso.individuo = individuo
        #Si individuo tiene atributo laboral damos permiso permanente:
        atributos = individuo.atributos.filter(tipo__in=('AS','PS','FP'))
        if atributos:
            atributo = atributos.first()        
            permiso.tipo = 'P'
            permiso.localidad = individuo.domicilio_actual.localidad
            permiso.begda = timezone.now()
            permiso.endda = LAST_DATETIME
            permiso.aclaracion = "Permiso Permanente: " + atributo.get_tipo_display()
            permiso.save()
    #Generamos siempre variable temporal:
    permiso.aprobar = True
    return permiso

def dia_permitido(num_doc):#Definir con DNIS
    #Tenemos que mejorar sistema de configuracion de DNIS
    return timezone.now() + timedelta(days=1)

def horario_libre(nivel, permiso, fecha_ideal):
    #Aca tenemos que tener en cuenta los horarios nivel.inicio_horario hasta nivel.cierre_horario
    #Generamos posibles segmentos
    segmentos = []
    while nivel.inicio_horario < (nivel.cierre_horario - nivel.duracion_permiso):
        segmentos.append(time(nivel.inicio_horario))
        nivel.inicio_horario+=1
    #Analizamos en ESA localidad

    #Analizamos horario ideal

    #Si es el mas cargado, analizamos otros

    #Asignamos mejor opcion

    #Devolvemos permiso con Mejor opcion
    return permiso

#Validamos la posibilidad de otorgar el permiso
def validar_permiso(individuo, permiso):
    nivel = nivel_restriccion_actual()
    #Todo permiso esta aprobado hasta que se demuestre lo contrario:
    #iniciamos chequeos
    permiso.localidad = individuo.domicilio_actual.localidad
    #Chequeamos que no este en cuarentena obligatoria o aislado
    if individuo.situacion_actual.conducta in ('D', 'E'):
        permiso.aprobar = False
        permiso.aclaracion = "Usted se encuentra bajo " + individuo.situacion_actual.get_conducta_display() + " Mantengase en su Hogar."
        return permiso#ya retornamos permiso denegado
    #Apartamos Fecha y Hora Requerida
    fecha_ideal = permiso.begda
    #Entregamos Permiso por Control DNI:
    permiso.begda = dia_permitido(individuo.num_doc)#Aca elegir por dia de DNI
    #Asignamos turno del dia que este menos ocupado
    permiso = horario_libre(nivel, permiso, fecha_ideal)
    #Aplicamos la duracion valida
    permiso.endda = permiso.begda + timedelta(hours=nivel.duracion_permiso)
    #Chequeamos Otras cosas(?)

    #HARDCODEADO HASTA QUE SE APRUEBE:
    permiso.aprobar = False
    permiso.aclaracion = "Esta Funcionalidad aun no fue Aprobada. Sigue Vigente Permiso Nacional."
    #Funcionar
    return permiso

def json_permiso(permiso, vista):
    return JsonResponse(
            {
                "action": vista,
                "realizado": True,
                "tipo_permiso": permiso.get_tipo_display(),
                "dni_individuo": permiso.individuo.num_doc,
                "nombre_completo": permiso.individuo.apellidos + ', ' + permiso.individuo.nombres,
                "domicilio": permiso.individuo.domicilio_actual.nombre_corto(),
                "fecha_inicio": permiso.begda.date(),
                "hora_inicio": permiso.begda.time(),
                "fecha_fin": permiso.endda.date(),
                "hora_fin": permiso.endda.time(),
                "imagen": permiso.individuo.get_foto(),
                "qr": permiso.individuo.get_qr(),
                "control": permiso.individuo.controlador(),
                "texto": permiso.aclaracion,

            },
            safe=False
        )

def horario_activo():
    ahora = timezone.now().time()
    if ahora > TIME_INICIO and  ahora < TIME_FIN:
        return True