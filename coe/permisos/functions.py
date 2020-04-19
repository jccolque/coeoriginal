#Imports de Python
from datetime import timedelta
#Imports de Django
from django.utils import timezone
from django.http import JsonResponse
#Imports Extras
#Imports del proyecto
from coe.constantes import LAST_DATETIME
from informacion.models import Individuo
#Imports de la app
from .models import Permiso

#Funciones
def actualizar_individuo(form):
    individuo = form.save(commit=False)
    try:
        individuo_db = Individuo.objects.get(num_doc=individuo.num_doc)
        #Cargamos todos los datos nuevos utiles:
        individuo_db.sexo = individuo.sexo
        individuo_db.fecha_nacimiento = individuo.fecha_nacimiento
        individuo_db.nacionalidad = individuo.nacionalidad
        individuo_db.telefono = individuo.telefono
        individuo_db.email = individuo.email
        #Podriamos chequear que no este en cuarentena obligatoria/aislamiento
    except Individuo.DoesNotExist:
        individuo_db = individuo
    #Guardamos los datos conseguidos
    individuo_db.save()
    return individuo_db

#Salvoconducos
def buscar_permiso(individuo, activo=False):
    permisos = Permiso.objects.filter(individuo=individuo, endda__gt=timezone.now())
    permisos = permisos.select_related('individuo', 'individuo__domicilio_actual')
    if activo:#Chequear que este activo
        permisos = permisos.filter(begda__lt=timezone.now())
    permiso = permisos.first()
    if not permiso:
        #Chequeamos que el individuo no tenga atributo laboral para permiso permanente:
        atributos = individuo.atributos.filter(tipo__in=('AS','PS','FP'))
        if atributos:
            atributo = atributos.first()
            permiso = Permiso()
            permiso.individuo = individuo
            permiso.tipo = 'P'
            permiso.localidad = individuo.domicilio_actual.localidad
            permiso.begda = timezone.now()
            permiso.endda = LAST_DATETIME
            permiso.aclaracion = "Permiso Permanente: " + atributo.get_tipo_display()
            permiso.control = True
            permiso.save()
    if permiso:
        permiso.aprobar = True
    return permiso

#Validamos la posibilidad de otorgar el permiso
def pedir_permiso(individuo, tipo_permiso, permiso=None):
    #Inicializamos permiso:
    if permiso:#Si encontro un permiso previamente guardado
        permiso.aprobar = True
    else:
        permiso = Permiso()
        permiso.aprobar = True
        permiso.localidad = individuo.domicilio_actual.localidad
        permiso.controlador = individuo.controlador_salvoconducto()
        #REALIZAR TODA LA LOGICA
        #Chequeamos que no este en cuarentena obligatoria o aislado
        if individuo.situacion_actual.conducta in ('D', 'E'):
            permiso.aprobar = False
            permiso.aclaracion = "Usted se encuentra bajo " + individuo.situacion_actual.get_conducta_display() + " Mantengase en su Hogar."
        else:
            #Chequeamos que no tenga un permiso hace menos de 3 dias
            cooldown = timezone.now() - timedelta(days=3)
            permisos = individuo.permisos.filter(endda__gt=cooldown)#, tipo=tipo_permiso)#(DEL MISMO TIPO?):
            if permisos:
                permiso.aprobar = False
                permiso.aclaracion = "Usted recibio un Permiso el dia " + str(permisos.last().endda.date())
            else:
                #Chequeamos que nadie del domicilio tenga permiso
                for relacion in individuo.relaciones.filter(tipo="MD"):
                    if relacion.relacionado.permisos.filter(endda__gt=cooldown, tipo=tipo_permiso):
                        relacionado = relacion.relacionado
                        permiso.aprobar = False
                        permiso.aclaracion = relacionado.nombres + ' ' + relacionado.apellidos + ' Ya obtuvo un permiso en los ultimos dias.' 
        #Devolvemos todo lo procesado
        #HARDCODEADO HASTA QUE SE APRUEBE:
        permiso.aprobar = False
        permiso.aclaracion = "Esta Funcionalidad aun no fue Aprobada. Sigue Vigente Permiso Nacional."
        #Funcionar
    return permiso

#Aca ordenamos por zonas y tiempos
def definir_fechas(permiso, fecha_ideal):
    #Agregar Control DNI por dias
    #Aca tenemos que poner los horarios de comercio/fabricas
    #Aca tenemos que poner controles por zona (Podriamos usar su ultima posicion gps conocida)
    permiso.begda = timezone.now() + timedelta(days=1)
    permiso.endda = timezone.now() + timedelta(days=1, hours=2)
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
                "control": permiso.controlador,
                "texto": permiso.aclaracion,

            },
            safe=False
        )