#Import Django
from django.db import models
from django.core.cache import cache
#Imports de la app
from .choices import TIPO_GRAFICO

# Create your models here.
class Grafico(models.Model):
    nombre = models.CharField('Nombre Informatico', max_length=100)
    verbose_name = models.CharField('Nombre Para Mostrar', max_length=100)
    tipo = models.CharField('Tipo Grafico', choices=TIPO_GRAFICO, max_length=2, default='L')
    update = models.DateField('Ultimo Dato Cargado', null=True)
    cant_datos = models.IntegerField('Cantidad de Datos a Mostrar', default=15)
    publico = models.BooleanField(default=False)
    def __str__(self):
        return self.nombre + ': ' + str(self.update)
    def agregar_dato(self, update_date, columna_nombre, fila, valor):
        #Buscamos/Creamos la columna
        try:
            columna = [c for c in self.columnas.all() if c.nombre == columna_nombre][0]
        except Columna.DoesNotExist:
            cant = self.columnas.count() + 1
            columna = Columna(grafico=self, orden=cant, nombre=columna_nombre)
            columna.save()
        #Eliminamos si habia un dato en esa "celda"
        columna.datos.filter(fila=fila).delete()
        #Agregamos el dato:
        dato = Dato()
        dato.grafico = self
        dato.columna = columna
        dato.fila = fila
        dato.valor = valor
        dato.save()
        #Informamos que fue Actualizado
        self.update = update_date
        self.save()
    def reiniciar_datos(self):
        cache.set(self.nombre, [])
        Dato.objects.filter(columna__grafico=self).delete()
    def bulk_dato(self, update_date, columna_nombre, fila, valor):
        #Buscamos/Creamos la columna
        try:
            columna = [c for c in self.columnas.all() if c.nombre == columna_nombre][0]
        except Columna.DoesNotExist:
            cant = self.columnas.count() + 1
            columna = Columna(grafico=self, orden=cant, nombre=columna_nombre)
            columna.save()
        #Agregamos el dato:
        dato = Dato()
        dato.grafico = self
        dato.columna = columna
        dato.fila = fila
        dato.valor = valor
        #Lo mandamos a la cache
        datos = cache.get(self.nombre)
        datos.append(dato)
        cache.set(self.nombre, datos)
    def bulk_save(self):
        datos = cache.get(self.nombre)
        self.reiniciar_datos()
        Dato.objects.bulk_create(datos)
    def cabecera(self):
        #Obtenemos todo lo necesario para procesar
        return ['Fecha'] + [c.nombre for c in self.columnas.all() if c.mostrar == True]
    def obtener_datos(self):
        #Para graficos de Lineas
        if self.tipo in ('L', 'C'):
            #Traemos todo el bloque de datos ya indexado
            dict_datos = {}
            for columna in self.columnas.all():
                if columna.mostrar:
                    for dato in columna.datos.all():
                        dict_datos[dato.columna.nombre,dato.fila] = dato
            #Referencias disponibles
            if self.columnas.all():#Si tiene columnas
                filas = [d.fila for d in  self.columnas.first().datos.all()]
                #Creamos nuestro vector
                datos = []
                for fila in filas:#Por cada Fecha
                    #Generamos cada linea
                    dato = []
                    for columna in self.cabecera()[1:]:
                        try:
                            dato.append(dict_datos[columna,fila])
                        except KeyError:#Si faltan datos por columna vacia
                            new = Dato()#Lo creamos con valor 0
                            new.columna = self.columnas.get(nombre=columna)
                            new.fila = fila
                            new.valor = 0
                            new.save()
                            dato.append(new)
                    #Agregamos la linea
                    datos.append(dato)
                return datos[-int(self.cant_datos):]#Entregamos la cantidad esperada
        #Para Graficos de Torta
        elif self.tipo == 'P':
            datos = self.columnas.first().datos.all()#Solo es una columna
            datos = datos.order_by('-valor')
            return [d for d in  datos][:self.cant_datos]#De mayor a menor

class Columna(models.Model):
    grafico = models.ForeignKey(Grafico, on_delete=models.CASCADE, related_name="columnas")
    nombre = models.CharField('Nombre', max_length=50)
    orden = models.IntegerField('Orden')
    mostrar = models.BooleanField(default=True)
    class Meta:
        ordering = ['-mostrar', 'orden']
    def __str__(self):
        return self.nombre

class Dato(models.Model):
    columna = models.ForeignKey(Columna, on_delete=models.CASCADE, related_name="datos")
    fila = models.CharField('Fila', max_length=100, null=True)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2)
    class Meta:
        ordering = ['pk', ]
    def __str__(self):
        return self.fila + '-' + self.columna.nombre + ' Cant: ' + str(self.valor) 

