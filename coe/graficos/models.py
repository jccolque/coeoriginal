#Import Django
from django.db import models
from django.utils import timezone
#Imports de la app
from .choices import TIPO_GRAFICO

# Create your models here.
class Grafico(models.Model):
    nombre = models.CharField('Nombre Informatico', max_length=100)
    verbose_name = models.CharField('Nombre Para Mostrar', max_length=100)
    tipo = models.CharField('Tipo Grafico', choices=TIPO_GRAFICO, max_length=1, default='L')
    update = models.DateField('Ultimo Dato Cargado', null=True)
    columnas = models.CharField('Columnas a Mostrar', max_length=250, null=True)
    publico = models.BooleanField(default=False)
    def __str__(self):
        return self.nombre + ': ' + str(self.update)
    def agregar_dato(self, update_date, nombre, ref, valor):
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
        self.update = update_date
        self.save()
    def cabecera(self):
        #Obtenemos todo lo necesario para procesar
        if self.columnas:
            return ['Fecha'] + self.columnas.split(';')
        else:
            return ['Fecha'] + list(self.datos.values_list('nombre', flat=True).distinct())
    def obtener_datos(self):
        #Obtenemos todo lo necesario para procesar
        nombres = self.cabecera()[1:]
        #Referencias disponibles
        refs = list(self.datos.values_list('ref', flat=True).distinct())
        #Traemos todo el bloque de datos ya indexado
        dict_datos = {(d.nombre,d.ref):d for d in self.datos.all()}
        #Creamos nuestro vector
        datos = []
        for ref in refs:#Por cada Fecha
            #Generamos cada linea
            dato = []
            for nombre in nombres:
                dato.append(dict_datos[(nombre, ref)])
            #Agregamos la linea
            datos.append(dato)
        return datos

class Dato(models.Model):
    grafico = models.ForeignKey(Grafico, on_delete=models.CASCADE, related_name="datos")
    nombre = models.CharField('Nombre', max_length=50)
    ref = models.CharField('Referencia', max_length=100, null=True)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    def __str__(self):
        return self.nombre + ' ref: ' + self.ref + ' Cant: ' + str(self.valor) 

