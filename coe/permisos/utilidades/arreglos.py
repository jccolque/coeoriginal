#Imports Extras

#Imports de la app
from permisos.models import IngresoProvincia

def recuperar_operadores():
    ingresos = IngresoProvincia.objects.filter(estado='A', operador=None)
    for ingreso in ingresos:
        