from __future__ import unicode_literals
#Imports Standard de python
#Import standard de Djagno
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
#Import Extras
from tinymce.models import HTMLField
from taggit.managers import TaggableManager
from auditlog.registry import auditlog
#Imports del proyecto
from coe.settings import LOADDATA
#Imports de la app

#Create your models here.
class Noticia(models.Model):
    titulo = models.CharField('Titulo', max_length=200)
    portada = models.FileField(upload_to='noticias/', default='/static/img/noimage.png')
    epigrafe = models.CharField('Epigrafe', default='imagen' ,max_length=100)
    etiquetas = TaggableManager()
    cuerpo = HTMLField()
    fecha = models.DateTimeField('Fecha', default=timezone.now)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    destacada = models.BooleanField(default=False)
    #ubicacion = ciudades? 
    def __str__(self):
        return self.titulo
    def as_dict(self):
        return {
            'id': self.id,
            'titulo':  self.titulo,
            'portada': str(self.portada),
            'epigrafe': self.epigrafe,
            'etiquetas': str(self.etiquetas.all()),
            'cuerpo': self.cuerpo,
            'fecha': str(self.fecha),
            'autor': str(self.autor),
            'destacada': self.destacada,
        }


class Parte(models.Model):
    title = models.CharField(
        'Título', 
        max_length=200
    )
    photo = models.FileField(
        'Foto',
        upload_to='partes/',
        default='/static/img/noimage.png'
    )
    epigraph = models.CharField(
        'Epigrafe', 
        default='imagen', 
        max_length=100
    )
    etiquetas = TaggableManager()
    cuerpo = HTMLField()
    fecha = models.DateTimeField(
        'Fecha', 
        default=timezone.now
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    destacada = models.BooleanField(default=False)     
    def __str__(self):
        return self.title
    def as_dict(self):
        return {
            'id': self.id,
            'title':  self.title,
            'photo': str(self.photo),
            'epigraph': self.epigraph,
            'etiquetas': str(self.etiquetas.all()),
            'cuerpo': self.cuerpo,
            'fecha': str(self.fecha),
            'author': str(self.author),
            'destacada': self.destacada,
        }

if not LOADDATA:
    #Auditoria
    auditlog.register(Noticia)
    auditlog.register(Parte)