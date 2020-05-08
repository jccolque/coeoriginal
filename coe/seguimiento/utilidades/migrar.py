#Imports del proyecto
from informacion.models import Seguimiento as Segs_Viejos
from seguimiento.models import Seguimiento as Segs_Nuevos

#Realizamos la migracion
def migrar_seguimientos():
    segs_viejos = Segs_Viejos.objects.all()
    print("Seguimientos Viejos: " + str(segs_viejos.count()))
    segs_viejos = list(segs_viejos)
    Segs_Nuevos.objects.bulk_create(segs_viejos)
    print("Seguimientos Nuevos: " + str(Segs_Nuevos.objects.count()))