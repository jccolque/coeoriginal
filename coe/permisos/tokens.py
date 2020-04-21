#Imports de Python
import string
import random
#Imports de Django
from django.utils import timezone
#Imports de la app

#Definimos nuestras funciones
def ct_timestamp():
    return str(timezone.now().timestamp()).split('.')[1]

def generar_token():
    return ct_timestamp()+''.join(random.sample(string.ascii_uppercase + string.digits, k=25))