#Imports Extras
from auditlog.models import LogEntry
#Imports del proyecto
from operadores.models import Operador
from permisos.models import IngresoProvincia
from beneficiarios.models import Domicilio as Domicilio_benef
from empresas.models import Domicilio as Domicilio_empre
from establecimientos.models import Sede
from georef.models import Departamento, Localidad, Barrio

#Solucionar error de duplicidad de elementos
def eliminar_deptos_repetidos():
    for depto in Departamento.objects.all():
        repetidas = Departamento.objects.filter(nombre=depto.nombre)
        if repetidas.count() > 1:
            original = repetidas.first()
            for r in repetidas.exclude(id=original.id):
                Localidad.objects.filter(departamento=r).update(departamento=original)
                r.delete()    

def eliminar_localidades_repetidas():
    for l in Localidad.objects.all():
        repetidas = Localidad.objects.filter(nombre=l.nombre)
        if repetidas.count() > 1:
            original = repetidas.first()
            for r in repetidas.exclude(id=original.id):
                Domicilio_benef.objects.filter(localidad=r).update(localidad=original)
                Domicilio_empre.objects.filter(localidad=r).update(localidad=original)
                Sede.objects.filter(localidad=r).update(localidad=original)
                Barrio.objects.filter(localidad=r).update(localidad=original)
                r.delete()

def eliminar_barrios_repetidos():
    for barrio in Barrio.objects.all():
        repetidas = Barrio.objects.filter(nombre=barrio.nombre)
        if repetidas.count() > 1:
            original = repetidas.first()
            for r in repetidas.exclude(id=original.id):
                Domicilio_benef.objects.filter(barrio=r).update(barrio=original)
                Sede.objects.filter(barrio=r).update(barrio=original)
                r.delete()

#Solucionar Falla por Operadores que no se cargaron antes
def recuperar_operadores():
    ingresos = IngresoProvincia.objects.filter(estado='A', operador=None)
    for ingreso in ingresos:
        print(str(ingreso)+' No tiene Operador.')
        regs = LogEntry.objects.filter(
            object_id=ingreso.pk,
            content_type__model="ingresoprovincia"
        )
        for reg in regs.all():
            if 'estado' in reg.changes_dict and reg.changes_dict['estado'][1] == 'A':
                print('El que aprobo fue: '+str(reg.actor))
                ingreso.operador = reg.actor.operadores.first()
                ingreso.save()
