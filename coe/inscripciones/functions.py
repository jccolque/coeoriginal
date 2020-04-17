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
    #Creamos nuevo domicilio
    domicilio = Domicilio()
    domicilio.individuo = individuo_db
    domicilio.localidad = form.dom_localidad
    domicilio.calle = form.dom_calle
    domicilio.numero = form.dom_numero
    domicilio.aclaracion = 'Inscripcion:' + form.dom_aclaracion
    domicilio.save()
    #Al terminar devolvemos individuo
    return individuo_db
