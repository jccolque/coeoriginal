#Imports de django
from django.utils import timezone
#imports de la app
from informacion.models import Individuo
from informacion.models import Domicilio, Situacion
from seguimiento.models import Seguimiento

def domicilios_actuales():
    #Actualizamos Domicilios
    individuos_to_update = []
    #Obtenemos individuos sin domicilio actual
    individuos = Individuo.objects.filter(domicilio_actual=None)
    print("\nIndividuos que deben ser reparados:", individuos.count())
    print("Generando dict de Domicilios. Inicio:", timezone.now())
    domicilios = {d.individuo.id:d for d in Domicilio.objects.filter(individuo__in=individuos).order_by('fecha').select_related('individuo')}
    print("Dict Generado, obtuvimos:", len(domicilios), "Registros para cargar.")
    indice = 0
    for d in domicilios.values():
        indice += 1
        if (indice % 1000) == 0:
            print("Se procesaron:", indice, "Registros. Time:", timezone.now())
            Individuo.objects.bulk_update(individuos_to_update, ['domicilio_actual'])
            print("Llevamos procesados", int((100.0/len(domicilios))*indice), '%')
            individuos_to_update = []
        #Lo cargamos
        d.individuo.domicilio_actual = d
        individuos_to_update.append(d.individuo)
    #MAndamos bulk update
    print("Se procesaron:", indice, "Registros")
    Individuo.objects.bulk_update(individuos_to_update, ['domicilio_actual'])
    print("Terminamos el Bulk Update. Time:", timezone.now())

def situaciones_actuales():
    #Actualizamos situaciones:
    individuos_to_update = []
    #Obtenemos individuos sin situacion
    individuos = Individuo.objects.filter(situacion_actual=None)
    print("\nIndividuos que deben ser reparados:", individuos.count())
    print("Generando dict de Situaciones. Inicio:", timezone.now())
    situaciones = {s.individuo.id:s for s in Situacion.objects.filter(individuo__in=individuos).order_by('fecha').select_related('individuo')}
    print("Dict Generado, obtuvimos:", len(situaciones), "Registros para cargar.")
    indice = 0
    for s in situaciones.values():
        indice += 1
        if (indice % 1000) == 0:
            print("Se procesaron:", indice, "Registros. Time:", timezone.now())
            #Creamos masivamente las situaciones que faltaban
            Individuo.objects.bulk_update(individuos_to_update, ['situacion_actual'])
            print("Llevamos procesados", int((100.0/len(situaciones))*indice), '%')
            individuos_to_update = []
        #Lo cargamos
        s.individuo.situacion_actual = s
        individuos_to_update.append(s.individuo)
    #Mandamos bulk update
    print("Se procesaron:", indice, "Registros")
    Individuo.objects.bulk_update(individuos_to_update, ['situacion_actual'])
    print("Terminamos el Bulk Update. Time:", timezone.now())

def seguimientos_actuales():
    individuos_to_update = []
    individuos = Individuo.objects.filter(seguimiento_actual=None)
    print("\nIndividuos que deben ser reparados:", individuos.count())
    print("Generando dict de seguimientos. Inicio:", timezone.now())
    seguimientos = {s.individuo.id:s for s in Seguimiento.objects.filter(individuo__in=individuos).order_by('fecha').select_related('individuo')}
    print("Dict Generado, obtuvimos:", len(seguimientos), "Registros para cargar.")
    indice = 0
    for s in seguimientos.values():
        indice += 1
        if (indice % 1000) == 0:
            print("Se procesaron:", indice, "Registros. Time:", timezone.now())
            Individuo.objects.bulk_update(individuos_to_update, ['seguimiento_actual'])
            print("Llevamos procesados", int(100/len(seguimientos))*indice, '%')
            individuos_to_update = []
        #Lo cargamos
        s.individuo.seguimiento_actual = s
        individuos_to_update.append(s.individuo)
    #MAndamos bulk update
    print("Se procesaron:", indice, "Registros")
    Individuo.objects.bulk_update(individuos_to_update, ['seguimiento_actual'])
    print("Terminamos el Bulk Update. Time:", timezone.now())

def fabricar_situaciones():
    #Nos aseguramos que los que tienen sin cargar se las cargue:
    situaciones_actuales()
    #Obtenemos todos los que no tienen
    individuos = Individuo.objects.filter(situacion_actual=None)
    print("\nIndividuos a los que debemos crearle Situaciones:", individuos.count())
    #Generamos nuevas situaciones
    indice = 0
    situaciones = []
    for i in individuos:
        indice += 1
        sit = Situacion(individuo=i)
        sit.aclaracion = "Generada automaticamente por sistema bulk_update"
        #La agregamos a listado
        situaciones.append(sit)
        #Vamos procesando de a bloques:
        if len(situaciones) == 10000:
            Situacion.objects.bulk_create(situaciones)
            print("Se Crearon:", indice, "Registros. Time:", timezone.now())
            situaciones = []
    print("Ultimo Procesamiento:", len(situaciones), "Registros\n")
    Situacion.objects.bulk_create(situaciones)
    #Lanzamos la asignacion Total
    situaciones_actuales()