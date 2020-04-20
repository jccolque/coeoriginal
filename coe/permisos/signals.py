#Imports Python
import logging
#Imports Django
from django.dispatch import receiver
from django.db.models.signals import post_save
#imports Extras
#Imports de la app
from .models import IngresoProvincia

#Logger
logger = logging.getLogger('signals')