#Imports de python
from datetime import timedelta
#Import Django
from django.utils import timezone
#Imports del proyecto
from coe.constantes import DIAS_CUARENTENA
from informacion.models import Individuo
from informacion.models import Situacion, Domicilio, Sintoma, Atributo
from geotracking.models import GeoPosicion
from app.models import AppData
from seguimiento.models import Seguimiento

#Funciones
def eliminar_aislamientos_duplicados():
    aislados = Individuo.objects.filter(situacion_actual__conducta__in=('D', 'E'))
    aislados = aislados.select_related('situacion_actual')
    aislados = aislados.prefetch_related('situaciones')
    #Recorremos los aislados
    for aislado in aislados:
        #Verificamos los que tienen mas de un aislamiento
        if sum([1 for s in aislado.situaciones.all() if s.conducta == 'D' or s.conducta == 'E']) > 1:
            sit_original = aislado.situaciones.filter(conducta__in=('D','E')).order_by('fecha').first()
            print("Arreglamos a: " + str(aislado))
            aislado.situacion_actual.fecha = sit_original.fecha
            aislado.situacion_actual.save()
            aislado.situaciones.filter(conducta__in=('D','E')).exclude(pk=aislado.situacion_actual.pk).delete()
            
def bajas_automaticas():
    individuos = Individuo.objects.filter(situacion_actual__conducta__in=('D', 'E'))
    #Obtenemos todos los que ya llevan 16 dias de cuarentena
    limite = timezone.now() - timedelta(days=DIAS_CUARENTENA + 2)
    individuos = individuos.filter(situacion_actual__fecha__lt=limite)
    #Los damos de baja a la fuerza:
    for individuo in individuos:
        print("Sacamos de Aislamiento pk:" + str(individuo.pk) + ' - ' + str(individuo))
        #Lo quitamos de Seguimiento
        seguimiento = Seguimiento(individuo=individuo)
        seguimiento.tipo = 'FS'
        seguimiento.aclaracion = "Baja automatizada"
        seguimiento.save()
        #Lo damos de Alta de Aislamiento
        situacion = Situacion(individuo=individuo)
        seguimiento.aclaracion = "Baja automatizada"
        situacion.save()
        #Le cambiamos el domicilio
        dom = individuo.domicilios.filter(aislamiento=False).last()#Buscamos el ultimo conocido comun
        if not dom:#Si no existe
            dom = individuo.domicilio_actual#usamos el de aislamiento
            dom.ubicacion = None#Pero blanqueado
            dom.aislamiento = False
            dom.numero += '(pk:' + str(individuo.pk) + ')'#Agregamos 'salt' para evitar relaciones
        #Blanqueamos campos para crearlo como nuevo:
        dom.pk = None
        dom.aclaracion = "Baja automatizada"
        dom.fecha = timezone.now()
        dom.save()

#Vamos a limpiar todos los repetidos que no sean actual
def limpiar_situacion():
    actuales = [i['situacion_actual'] for i in Individuo.objects.exclude(situacion_actual=None).values('situacion_actual')]
    situaciones = Situacion.objects.exclude(id__in=actuales)
    situaciones = situaciones.select_related('individuo')
    situaciones = situaciones.order_by('-fecha')
    #Stacks
    guardar = {}
    eliminar = []
    #Procesamos
    for s in situaciones:
        if (s.individuo.id, s.estado, s.conducta) not in guardar:
            guardar[(s.individuo.id, s.estado, s.conducta)] = s
        else:
            eliminar.append(s.id)
    Situacion.objects.filter(id__in=eliminar).delete()
    print("Se eliminaron", len(eliminar), "Situaciones Repetidos.")

def limpiar_domicilios():
    actuales = [i['domicilio_actual'] for i in Individuo.objects.exclude(domicilio_actual=None).values('domicilio_actual')]
    domicilios = Domicilio.objects.exclude(id__in=actuales)
    domicilios = Domicilio.objects.exclude(aclaracion="PADRON")
    domicilios = domicilios.select_related('individuo')
    domicilios = domicilios.order_by('-fecha')
    #Stacks
    guardar = {}
    eliminar = []
    #Procesamos
    for d in domicilios:
        if (d.individuo.id, d.calle, d.numero) not in guardar:
            guardar[(d.individuo.id, d.calle, d.numero)] = d
        else:
            eliminar.append(d.id)
    Domicilio.objects.filter(id__in=eliminar).delete()
    print("Se eliminaron", len(eliminar), "Domicilios Repetidos.")


def limpiar_sintomas():
    sintomas = Sintoma.objects.all()
    sintomas = sintomas.select_related('individuo')
    sintomas = sintomas.order_by('fecha')
    #Stacks
    guardar = {}
    eliminar = []
    #Procesamos
    for s in sintomas:
        if (s.individuo.id, s.tipo) not in guardar:
            guardar[(s.individuo.id, s.tipo)] = s
        else:
            eliminar.append(s.id)
    Sintoma.objects.filter(id__in=eliminar).delete()
    print("Se eliminaron", len(eliminar), "Sintomas Repetidos.")

def limpiar_atributos():
    atributos = Atributo.objects.all()
    atributos = atributos.select_related('individuo')
    atributos = atributos.order_by('fecha')
    #Stacks
    guardar = {}
    eliminar = []
    #Procesamos
    for a in atributos:
        if (a.individuo.id, a.tipo) not in guardar:
            guardar[(a.individuo.id, a.tipo)] = a
        else:
            eliminar.append(a.id)
    Atributo.objects.filter(id__in=eliminar).delete()
    print("Se eliminaron", len(eliminar), "Atributos Repetidos.")

def remplazar_esperando_res():
    for atributo in Atributo.objects.filter(tipo='ER'):
        seguimiento = Seguimiento()
        seguimiento.individuo = atributo.individuo
        seguimiento.tipo = 'ET'
        seguimiento.fecha = atributo.fecha
        seguimiento.aclaracion = 'MIGRADO:' + str(atributo.aclaracion)
        seguimiento.save()
        atributo.delete()


def borrar_appdata():
    AppData.objects.all().delete()
    Individuo.objects.filter(observaciones="AUTODIAGNOSTICO").delete()
    Situacion.objects.filter(aclaracion="AUTODIAGNOSTICO").delete()
    Domicilio.objects.filter(aclaracion="AUTODIAGNOSTICO").delete()
    Sintoma.objects.filter(aclaracion="ENCUESTAAPP").delete()
    Atributo.objects.filter(aclaracion="ENCUESTAAPP").delete()
    Seguimiento.objects.filter(tipo="A").delete()
    GeoPosicion.objects.filter(aclaracion__icontains=("TRACK", "DIAGNO")).delete()