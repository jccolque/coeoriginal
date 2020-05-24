#Imports Django
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
#Imports extras
from auditlog.models import LogEntry
#Imports del proyecto
from informacion.models import Individuo, Atributo
from operadores.models import Operador
#Imports de la app
from seguimiento.models import Seguimiento, Vigia
from seguimiento.functions import obtener_bajo_seguimiento

#Definiciones
def operador_seguimiento():
    ct_segs = ContentType.objects.get_for_model(Seguimiento)
    #OBtenemos todos los registros de creacion de seguimientos
    registros = LogEntry.objects.filter(content_type=ct_segs, action=0)
    #Evitamos los que no tienen usuario
    registros = registros.exclude(actor=None)
    print("Registros de Creacion para Actualizar: " + str(registros.count()))
    #Generamos la lista de elementos por cada usuario
    usuarios = {}
    for registro in registros:
        if registro.actor in usuarios:
            usuarios[registro.actor].append(registro.object_pk)#Agregamos otro pk para actualizar
        else:
            usuarios[registro.actor] = [registro.object_pk, ]#Inicializamos la lista de pks
    #Actualizamos
    for user, pks in usuarios.items():
        print(str(len(pks)) + " seguimientos realizados por: "+ str(user))
        operador = Operador.objects.get(usuario=user)
        Seguimiento.objects.filter(pk__in=pks).update(operador=operador)

def activar_vigilancia():
    #Obtenemos todos los que estan en Cuarentena Obligatoria / Aislamiento
    individuos = Individuo.objects.filter(situacion_actual__conducta__in=('D', 'E'))
    #Evitamos los que ya estan en vigilancia
    individuos = individuos.exclude(atributos__tipo='VE')
    #Optimizamos
    individuos = individuos.select_related('situacion_actual')
    #Generamos el atributo:
    atribs = []
    for individuo in individuos:
        atributo = Atributo(individuo=individuo)
        atributo.tipo = 'VE'
        atributo.fecha = individuo.situacion_actual.fecha
        atributo.aclaracion = "Recuperado Via Sistema (utilidades/recuperar)"
        atribs.append(atributo)
    #Creamos todos:
    Atributo.objects.bulk_create(atribs)

def asignar_vigilancia():
    activar_vigilancia()
    individuos = obtener_bajo_seguimiento()
    #No procesamos a los que ya estan bajo un vigia
    individuos = individuos.filter(vigiladores=None)
    print("Asignaremos: " + str(individuos.count()) + " individuos.")
    #Procesamos
    for individuo in individuos:
        print("Asignamos a " + str(individuo))
        try:
            nuevo_vigia = Vigia.objects.all().annotate(cantidad=Count('controlados')).order_by('cantidad').first()
            nuevo_vigia.controlados.add(individuo)
        except:
            print("No hay vigias")