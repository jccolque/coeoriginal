#Imports del proyecto
def clean_tests():
    from informacion.models import Individuo
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

def quitar_viejos():
    import csv
    from datetime import timedelta
    from django.utils import timezone
    from seguimiento.models import Vigia, Seguimiento
    #Instanciamos csv
    with open('archivos/'+str(timezone.now().date()).replace("-", "")+'_SegEliminados.csv', 'w', newline='') as csvfile:
        linewriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        linewriter.writerow(["NUM DOC", "APELLIDO", "NOMBRE", "TELEFONO", "FECHA INICIO", "TIPO", "CANT SEGUIMIENTOS"])
        #Generamos limite
        limite = timezone.now() - timedelta(days=14)
        #Generamos bulk de seguimientos
        seguimientos = []
        #Recorremos vigilantes:
        for vigia in Vigia.objects.exclude(tipo__in=('VM', 'AP')).prefetch_related('controlados'):
            #Recorremos todos los vigilados
            for controlado in vigia.controlados.all().prefetch_related('atributos'):
                atrib = controlado.atributos.filter(tipo=vigia.tipo).last()
                if atrib and atrib.fecha < limite:
                    linewriter.writerow(
                        [
                            controlado.num_doc, 
                            controlado.apellidos, 
                            controlado.nombres, 
                            controlado.telefono,        
                            atrib.fecha,
                            atrib.get_tipo_display(),
                            controlado.seguimientos.filter(tipo="L").count(),
                        ]
                    )
                    #Generamos seguimiento base
                    seg = Seguimiento(individuo=controlado)
                    seg.tipo = "FS"
                    seg.aclaracion = "Se dio baja automatica: " + atrib.get_tipo_display() + " orden: Diego Valdecanto."
                    seguimientos.append(seg)
                    #Lo damos de baja
                    vigia.del_vigilado(controlado)
        #Hacemos bulk masivo para que no llame signals:
        Seguimiento.objects.bulk_create(seguimientos)

def quitar_sin_telefono():
    from coe.constantes import NOTEL
    from seguimiento.models import Vigia, Seguimiento
    for vigia in Vigia.objects.all().prefetch_related('controlados'):
        for controlado in vigia.controlados.all():
            if controlado.telefono == NOTEL or controlado.telefono == "":
                seg = Seguimiento(individuo=controlado)
                seg.tipo = "TE"
                seg.aclaracion = "Limpieza Masiva, Requiere Carga de Telefono"
                seg.save()
                vigia.del_vigilado(controlado)