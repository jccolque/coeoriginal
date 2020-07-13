#Imports del proyecto
from seguimiento.models import Seguimiento, Vigia

#Realizamos la migracion
def migrar_seguimientos():
    from informacion.models import Seguimiento as Segs_Viejos
    from seguimiento.models import Seguimiento as Segs_Nuevos
    segs_viejos = Segs_Viejos.objects.all()
    print("Seguimientos Viejos: " + str(segs_viejos.count()))
    segs_viejos = list(segs_viejos)
    Segs_Nuevos.objects.bulk_create(segs_viejos)
    print("Seguimientos Nuevos: " + str(Segs_Nuevos.objects.count()))

def migrar_tipo_operador():
    Vigia.objects.filter(tipo="E").update(tipo="VE")
    Vigia.objects.filter(tipo="M").update(tipo="VM")
    Vigia.objects.filter(tipo="T").update(tipo="VT")