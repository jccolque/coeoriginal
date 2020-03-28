#Import Django
from django.db import models
from django.utils import timezone
#Imports de la app
from .choices import TIPO_GRAFICO

# Create your models here.
class Grafico(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    tipo = models.CharField('Tipo Grafico', choices=TIPO_GRAFICO, max_length=1, default='L')
    update = models.DateField('Ultimo Dato', null=True)
    publico = models.BooleanField(default=False)
    def __str__(self):
        return self.nombre + ': ' + str(self.update)
    def agregar_dato(self, nombre, ref, valor):
        #Eliminamos si tenemos que remplazar
        self.datos.filter(nombre=nombre, ref=ref).delete()
        #Agregamos el dato:
        dato = Dato()
        dato.grafico = self
        dato.nombre = nombre
        dato.ref = ref
        dato.valor = valor
        dato.save()
        #Informamos que fue Actualizado
        self.update = timezone.now()
        self.save()
    def obtener_datos(self, cant_datos=15):
        #Obtenemos todo lo necesario para procesar
        nombres = list(self.datos.values_list('nombre', flat=True).distinct())
        refs = list(self.datos.values_list('ref', flat=True).distinct())
        dict_datos = {(d.nombre,d.ref):d for d in self.datos.all()}
        #Creamos nuestro vector
        datos = []
        for linea in range(0, cant_datos):
            dato = []
            for ref in refs:
                for nombre in nombres:
                    dato.append(dict_datos[(nombre, ref)])
            datos.append(dato)
        return datos
    def cabecera(self):
        return str('Fecha' + list(self.datos.values_list('nombre', flat=True).distinct()))

class Dato(models.Model):
    grafico = models.ForeignKey(Grafico, on_delete=models.CASCADE, related_name="datos")
    nombre = models.CharField('Nombre', max_length=100)
    ref = models.CharField('Referencia', max_length=100, null=True)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    def __str__(self):
        return self.nombre + '-' + self.ref + str(self.valor) 

