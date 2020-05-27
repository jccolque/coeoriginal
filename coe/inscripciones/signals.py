#Imports Python
import logging
#Imports Django
from django.dispatch import receiver
from django.db.models.signals import pre_save
#imports Extras
#Imports de la app
from .models import Inscripcion
#Logger
logger = logging.getLogger('signals')