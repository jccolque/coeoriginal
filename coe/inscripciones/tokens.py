#Imports de Python
import uuid
import string
import random
#Imports de Django
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
#Import Personales

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, instancia, timestamp):
        return (
            six.text_type(instancia.pk) + six.text_type(timestamp)
        )

account_activation_token = TokenGenerator()

#Definimos nuestras funciones
def ct_timestamp():
    return str(timezone.now().timestamp()).split('.')[1]

def token_inscripcion():
    return ct_timestamp()+''.join(random.sample(string.ascii_uppercase + string.digits, k=25))

def token_provision():
    token = str(uuid.uuid4())
    return ct_timestamp() + token

def token_organizacion():
    token = str(uuid.uuid4())
    return ct_timestamp() + token
