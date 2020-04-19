#Imports del proyecto
from informacion.models import Individuo, Domicilio

def actualizar_individuo(form):
    individuo = form.save(commit=False)
    try:
        individuo_db = Individuo.objects.get(num_doc=individuo.num_doc)
        #Cargamos todos los datos nuevos utiles:
        individuo_db.sexo = individuo.sexo
        individuo_db.fecha_nacimiento = individuo.fecha_nacimiento
        individuo_db.nacionalidad = individuo.nacionalidad
        individuo_db.telefono = individuo.telefono
        individuo_db.email = individuo.email
    except Individuo.DoesNotExist:
        individuo_db = individuo
    #Guardamos los datos conseguidos
    individuo_db.save()
    #Creamos nuevo domicilio
    domicilio = Domicilio()
    domicilio.individuo = individuo_db
    domicilio.localidad = form.cleaned_data['dom_localidad']
    domicilio.calle = form.cleaned_data['dom_calle']
    domicilio.numero = form.cleaned_data['dom_numero']
    domicilio.aclaracion = 'Inscripcion:' + form.cleaned_data['dom_aclaracion']
    domicilio.save()
    #Al terminar devolvemos individuo
    return individuo_db
   