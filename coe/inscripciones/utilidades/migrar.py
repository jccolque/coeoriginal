#Imports del proyecto
from informacion.models import Documento
#Imports de la app
from inscripciones.models import Inscripcion

def migrar_archivos():
    for inscripto in Inscripcion.objects.all():
        #Obtenemos individuo
        individuo = inscripto.individuo
        #Creamos docs:
        if inscripto.frente_dni:
            documento = Documento(individuo=individuo)
            documento.tipo = 'DI'
            documento.archivo = inscripto.frente_dni
            documento.aclaracion = 'FRENTE'
            documento.save()
        if inscripto.reverso_dni:
            documento = Documento(individuo=individuo)
            documento.tipo = 'DI'
            documento.archivo = inscripto.reverso_dni
            documento.aclaracion = 'REVERSO'
            documento.save()
        if inscripto.archivo_titulo:
            documento = Documento(individuo=individuo)
            documento.tipo = 'TP'
            documento.archivo = inscripto.archivo_titulo
            documento.aclaracion = 'Titulo Profesional'
            documento.save()
        print('\nMigramos: ' + str(inscripto.individuo))
