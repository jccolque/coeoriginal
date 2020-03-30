#Imports del proyecto
from informacion.models import Domicilio#localidad
from informacion.models import Individuo#destino
#Imports de la app
from .models import Localidad

def eliminar_localidades_duplicadas():
    corregir = Domicilio.objects.filter(localidad__nombre__icontains='\n')
    
    
