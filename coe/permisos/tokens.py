#Imports de Python
import string
import random

#Definimos nuestras funciones
def token_ingreso():
    return ''.join(random.sample(string.ascii_uppercase + string.digits, k=25))