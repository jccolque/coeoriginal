#Imports del proyecto

#Realizamos la migracion
def migrar_denuncias():
    from denuncias.models import DenunciaAnonima as Denuncias_Viejas
    from consultas.models import DenunciaAnonima as Denuncias_Nuevas
    den_viejas = Denuncias_Viejas.objects.all()
    print("Denuncias Viejas: " + str(den_viejas.count()))
    den_viejas = list(den_viejas)
    Denuncias_Nuevas.objects.bulk_create(den_viejas)
    print("Denuncias Nuevas: " + str(Denuncias_Nuevas.objects.count()))