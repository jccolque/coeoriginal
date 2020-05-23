#Imports del proyecto
from informacion.models import Individuo

def clean_tests():
    #Buscamos todos los que pidieron el test
    individuos = Individuo.objects.filter(seguimientos__tipo='PT')
    print('Limpieza de ' + str(individuos.count()) + ' Individuos')
    #Los recorremos para limpieza:
    for individuo in individuos:
        print('procesamos a: ' + str(individuo)) 
        #Borramos patologias repetidas
        patologias = {p.tipo:p.pk for p in individuo.patologias.all().order_by('-fecha')}
        patologias = list(patologias.values())
        individuo.patologias.exclude(pk__in=patologias).delete()
        #Borramos atributos repetidos
        atributos = {a.tipo:a.pk for a in individuo.atributos.all().order_by('-fecha')}
        atributos = list(atributos.values())
        individuo.atributos.exclude(pk__in=atributos).delete()