#Import Python Standard
#Imports de Django
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
#Imports del proyecto
try:
    from coe.credenciales import SECRET_KEY
except ImportError:
    SECRET_KEY = ''
from core.forms import UploadCsvWithPass
#Imports de la app
from .models import Provincia, Departamento, Localidad

# Create your views here.
@staff_member_required
def upload_localidades(request):
    titulo = "Carga Masiva Geografica"
    form = UploadCsvWithPass()
    if request.method == "POST":
        form = UploadCsvWithPass(request.POST, request.FILES)
        if form.is_valid():
            file_data = form.cleaned_data['csvfile'].read().decode("utf-8")
            lines = file_data.split("\n")
            cant = 0
            #Limpiamos la base de datos:
            Provincia.objects.all().delete()
            p = Provincia(nombre="Jujuy")
            p.save()
            #GEneramos todos los elementos nuevos
            for linea in lines:
                cant += 1
                linea=linea.split(',')
                if linea[0]:
                    departamento = Departamento.objects.get_or_create(
                        provincia=p,
                        nombre= linea[1])[0]
                    localidad = Localidad.objects.get_or_create(
                        departamento= departamento,
                        nombre= linea[2])[0]
                    localidad.codigo_postal = linea[0]
                    localidad.save()
            return render(request, 'extras/upload_csv.html', {'count': len(lines), })
    #Inicial o por error
    return render(request, "extras/upload_csv.html", {'titulo': titulo, 'form': form, })