#Funciones:

def actualizar_operadores():
    from informacion.models import Individuo
    from operadores.models import Operador
    for op in Operador.objects.all():
        try:
            op.individuo = Individuo.objects.get(num_doc=op.num_doc)
            op.save()
            print("Asignamos individuo para: " + str(op))
            #Actualizamos individuo:
            op.individuo.fotografia = op.fotografia
            op.individuo.telefono = op.telefono
            op.individuo.email = op.email
            op.individuo.save()
        except:
            print(str(op) + "Inasignable.")