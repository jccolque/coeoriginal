from informacion.choices import TIPO_ATRIBUTO, TIPO_SINTOMA
from informacion.models import Atributo, TipoAtributo
from informacion.models import Sintoma, TipoSintoma
from seguimiento.models import Seguimiento

def unificar_atributos():
    old = TipoAtributo.objects.get(nombre='Mantener Seguimiento')
    new = TipoAtributo.objects.get(nombre='Vigilancia Epidemiologica')
    #Cambiamos los que no van:
    for atrib in Atributo.objects.filter(tipo=old):
        atrib.tipo = new
        atrib.save()    
    #Borramos los ingreso a la provincia, ahora son seguimientos > Cronologia
    for a in Atributo.objects.filter(tipo__nombre="Ingreso a la Provincia"):
        seg = Seguimiento()
        seg.individuo = a.individuo
        seg.tipo = "C"
        seg.aclaracion = 'Migrado:' + str(a.aclaracion)
        seg.save()
        a.delete()

def migrar_atributos():
    unificar_atributos()
    dict_atrib = {a[1]:a[0] for a in TIPO_ATRIBUTO}
    for atrib in Atributo.objects.all():
        atrib.newtipo = dict_atrib[atrib.tipo.nombre]
        atrib.save()

def unificar_sintomas():
    old = TipoSintoma.objects.get(nombre='Fiebre Alta')
    new = TipoSintoma.objects.get(nombre='Fiebre')
    for sintom in Sintoma.objects.filter(tipo=old):
        sintom.tipo = new
        sintom.save()

def migrar_sintomas():
    unificar_sintomas()
    dict_sintom = {s[1]:s[0] for s in TIPO_SINTOMA}
    for sintom in Sintoma.objects.all():
        sintom.newtipo = dict_sintom[sintom.tipo.nombre]
        sintom.save()