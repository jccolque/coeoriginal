#Imports de Python
from datetime import time, timedelta
#Imports de Django
from django.utils import timezone
from django.core.cache import cache
from django.http import JsonResponse
#Imports Extras
#Imports del proyecto
from coe.constantes import LAST_DATETIME, TIME_INICIO, TIME_FIN
from seguimiento.functions import es_operador_activo
#Imports de la app
from .models import NivelRestriccion, Permiso

#Funciones
def nivel_restriccion_actual():
    nivel_restriccion = cache.get("nivel_restriccion")
    if not nivel_restriccion:
        nivel_restriccion = NivelRestriccion.objects.filter(activa=True).first()
        cache.set("nivel_restriccion", nivel_restriccion)
    return nivel_restriccion

#Salvoconducos
def buscar_permiso(individuo, activo=False):
    #Buscamos si el individuo tiene algun permiso
    permisos = Permiso.objects.filter(individuo=individuo, endda__gt=timezone.now())
    permisos = permisos.select_related('individuo', 'individuo__domicilio_actual')
    permisos = permisos.order_by('begda')

    if activo:#Si es un chequeo (Solo mostrar si es activo)
        permisos = permisos.filter(begda__lt=timezone.now())#Solo aplica en control de permisos

    if permisos:#Obtenemos el mas actual:
        return  permisos.first()#lo entregamos

    else:#Si no tiene permisos activos
        #Buscamos si tiene alguno valido
        for atributo in individuo.atributos.all():
            if atributo.tipo in ('AS','PS','FP', 'EP', 'TE', 'VA', 'CT'):
                #Agente de Salud / Personal de Seguridad / Funcionario Publico / Empleado Publico / Empresa Estrategica
                permiso = Permiso(individuo = individuo)
                permiso.tipo = 'P'
                permiso.localidad = individuo.domicilio_actual.localidad
                permiso.begda = timezone.now()
                permiso.endda = LAST_DATETIME
                permiso.aclaracion = "Permiso Permanente: " + atributo.get_tipo_display()
                permiso.save()
                return permiso#Lo entregamos
    
    if es_operador_activo(individuo.num_doc):
        permiso = Permiso(individuo = individuo)
        permiso.tipo = 'T'
        permiso.localidad = individuo.domicilio_actual.localidad
        permiso.begda = timezone.now()
        permiso.endda = timezone.now() + timedelta(hours=12)#No deberia ser fijo, pero ya fue.
        permiso.aclaracion = "Operador Activo para Cazador360"
        permiso.save()
        return permiso#Lo entregamos

def dia_permitido(permiso):#Definir con DNIS
    #Obtenemos nivel de restriccion
    nivel = nivel_restriccion_actual()
    #Obtentemos terminacion de dni
    num_doc = permiso.individuo.num_doc[:-1]
    #Tenemos que mejorar sistema de configuracion de DNIS
    permiso.begda = timezone.now() + timedelta(days=1)

    #Devolvemos permiso
    return permiso

def horario_libre(permiso):
    #Obtenemos nivel de restriccion
    nivel = nivel_restriccion_actual()
    #Aca tenemos que tener en cuenta los horarios nivel.inicio_horario hasta nivel.cierre_horario
    #Generamos posibles segmentos
    segmentos = []
    while nivel.inicio_horario < (nivel.cierre_horario - nivel.duracion_permiso):
        segmentos.append(time(nivel.inicio_horario))
        nivel.inicio_horario+=1
    
    #Analizamos en ESA localidad
    localidad = permiso.individuo.domicilio_actual.localidad
    
    #Analizamos horario ideal > permiso.begda

    #Si es el mas cargado, analizamos otros

    #Asignamos mejor opcion
    
    #Aplicamos la duracion valida
    permiso.endda = permiso.begda + timedelta(hours=nivel.duracion_permiso)
    #Devolvemos permiso con Mejor opcion
    return permiso

#Validamos la posibilidad de otorgar el permiso
def validar_permiso(individuo, permiso):
    #Todo permiso esta aprobado hasta que se demuestre lo contrario:
    
    #Chequeamos TODOS los motivos por los que no deberiamos darle un permiso
    #Que no este en cuarentena obligatoria o aislado
    if individuo.situacion_actual.conducta in ('D', 'E'):
        #permiso.aclaracion = "Usted se encuentra bajo " + individuo.situacion_actual.get_conducta_display() + " Mantengase en su Hogar."
        return None#ya retornamos permiso denegado

    #Aplicamos control por terminacion del DNI:
    permiso = dia_permitido(permiso)

    #Asignamos turno del dia que este menos ocupado
    permiso = horario_libre(permiso)

    #Chequeamos Otras cosas(?)
    if permiso:
        permiso.save()
        return permiso

def json_permiso(permiso, vista):
    if permiso:
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
                    "control": es_operador_activo(permiso.individuo.num_doc) or permiso.individuo.controlador(),
                    "texto": permiso.aclaracion,

                },
                safe=False
            )
    else:
        return JsonResponse(
                {
                    "action": vista,
                    "realizado": False,
                    "error": "Esta funcionalidad no se encuentra habilitada.",
                },
                safe=False,
                status=400,
        )

def horario_activo():
    ahora = timezone.now().time()
    if ahora > TIME_INICIO and  ahora < TIME_FIN:
        return True
