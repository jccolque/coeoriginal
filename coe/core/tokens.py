#Imports de Django
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
#Import Personales

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, instancia, timestamp):
        return (
            six.text_type(instancia.pk) + six.text_type(timestamp)
        )

account_activation_token = TokenGenerator()