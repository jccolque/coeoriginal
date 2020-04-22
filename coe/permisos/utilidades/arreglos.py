#Imports Extras
from auditlog.models import LogEntry
#Imports de la app
from operadores.models import Operador
from permisos.models import IngresoProvincia

def recuperar_operadores():
    ingresos = IngresoProvincia.objects.filter(estado='A', operador=None)
    for ingreso in ingresos:
        print(str(ingreso)+' No tiene Operador.')
        regs = LogEntry.objects.filter(
            object_id=ingreso.pk,
            content_type__model="ingresoprovincia"
        )
        for reg in regs.all():
            if reg.changes_dict['estado'][1] == 'A':
                print('El que aprobo fue: '+str(reg.actor))
                ingreso.operador = reg.actor.operadores.first()
                ingreso.save()