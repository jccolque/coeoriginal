#Imports de Python
import string
import random
import uuid
#Imports de Django
from django.utils import timezone
#Imports de la app


#Definimos nuestras funciones
def ct_timestamp():
    return str(timezone.now().timestamp()).split('.')[1]

def token_provision():
    token = str(uuid.uuid4())
    return ct_timestamp() + token