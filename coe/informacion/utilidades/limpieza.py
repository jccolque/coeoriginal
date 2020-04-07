from informacion.models import Individuo
from informacion.models import Situacion, Domicilio, Sintoma, Atributo, Seguimiento
from informacion.models import AppData

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

def borrar_appdata():
    AppData.objects.all().delete()
    Individuo.objects.filter(aclaracion="AUTODIAGNOSTICO").delete()
    Situacion.objects.filter(aclaracion="AUTODIAGNOSTICO").delete()
    Domicilio.objects.filter(aclaracion="AUTODIAGNOSTICO").delete()
    Sintoma.objects.filter(aclaracion="ENCUESTAAPP").delete()
    Atributo.objects.filter(aclaracion="ENCUESTAAPP").delete()
    Seguimiento.objects.filter(tipo="A").delete()