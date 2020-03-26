#Viejo modelo
from core.models import Consulta as Old_Consulta
#Nuevo modelo
from .models import Consulta as New_Consulta
from .models import Respuesta as New_Respuesta

def migrar():
    old_cons = Old_Consulta.objects.all()
    for old_con in old_cons:
        new_con = New_Consulta()
        new_con.autor = old_con.autor
        new_con.email = old_con.email
        new_con.telefono = old_con.telefono
        new_con.asunto = old_con.asunto
        new_con.descripcion = old_con.descripcion
        new_con.fecha_consulta = old_con.fecha_consulta
        new_con.valida = old_con.valida
        new_con.respondida = old_con.respondida
        new_con.save()
        for old_resp in old_con.respuestas2.all():
            new_resp = New_Respuesta()
            new_resp.consulta = new_con
            new_resp.operador = old_resp.operador
            new_resp.respuesta = old_resp.respuesta
            new_resp.fecha = old_resp.fecha
            new_resp.save()
