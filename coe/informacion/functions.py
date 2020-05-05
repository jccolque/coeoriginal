#Imports del proyecto
from informacion.models import Individuo, Domicilio, Documento, Seguimiento

#Definimos nuestras funciones reutilizables
def obtener_relacionados(individuo, relaciones):
    if individuo.id not in relaciones:
        relaciones.add(individuo.id)
        for relacion in individuo.relaciones.select_related('individuo', 'relacionado').all():
            obtener_relacionados(relacion.relacionado, relaciones)
    return relaciones

def actualizar_individuo(form):
    #Instanciamos individuo
    individuo = form.save(commit=False)
    #Intentamos actualizarlo
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
    if 'dom_origen' in form.cleaned_data:
        seg = Seguimiento(individuo=individuo_db)
        seg.tipo = 'DF'
        seg.aclaracion = form.cleaned_data['dom_origen']
        seg.save()
    if 'dom_localidad' in form.cleaned_data:
        domicilio = Domicilio(individuo=individuo_db)
        domicilio.localidad = form.cleaned_data['dom_localidad']
        domicilio.calle = form.cleaned_data['dom_calle']
        domicilio.numero = form.cleaned_data['dom_numero']
        domicilio.aclaracion = 'Inscripcion:' + form.cleaned_data['dom_aclaracion']
        #Si tiene un domicilio actual no permitimos que lo cambie
        if individuo_db.domicilio_actual:
            Domicilio.objects.bulk_create([domicilio])#Bulkupdate no genera signals
        else:
            domicilio.save()#esto impacta sobre su domicilio_actual
    if 'frente_dni' in form.cleaned_data:
        doc = Documento(individuo=individuo_db)
        doc.tipo = 'DI'
        doc.archivo = form.cleaned_data['frente_dni']
        doc.aclaracion = "Frente: Inscripcion de Ingreso a Jujuy"
        doc.save()
    if 'reverso_dni' in form.cleaned_data:
        doc = Documento(individuo=individuo_db)
        doc.tipo = 'DI'
        doc.archivo = form.cleaned_data['reverso_dni']
        doc.aclaracion = "Reverso: Inscripcion de Ingreso a Jujuy"
        doc.save()
    #Al terminar devolvemos el individuo
    return individuo_db