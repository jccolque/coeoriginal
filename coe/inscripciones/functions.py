#Imports del proyecto
from informacion.models import Individuo, Domicilio

def actualizar_individuo(form):
    individuo = form.save(commit=False)
    try:
        individuo_db = Individuo.objects.get(num_doc=individuo.num_doc)
        #Podriamos chequear que no este en cuarentena obligatoria/aislamiento
    except Individuo.DoesNotExist:
        individuo.save()#Lo generamos con todos los datos del Fomulario
        individuo_db = individuo
        individuo_db.nombres = form.cleaned_data['nombres']
        individuo_db.apellidos = form.cleaned_data['apellidos']
    #Cargamos todos los datos que nos dio:
    individuo_db.sexo = form.cleaned_data['sexo']
    individuo_db.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
    #Datos personales
    individuo.nacionalidad = form.cleaned_data['nacionalidad']
    individuo.telefono = form.cleaned_data['telefono']
    individuo.email = form.cleaned_data['email']
    #Guardamos los datos conseguidos
    individuo.save()
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
