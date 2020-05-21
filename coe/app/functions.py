#Funciones basicas:
def obtener_dni(data):
    if "dni" in data:
        return str(data["dni"]).upper()
    else:
        return str(data["dni_individuo"]).upper()

#Funcionalidades
def activar_tracking(individuo):
    AppNotificacion.objects.filter(appdata=individuo.appdata).delete()
    notif = AppNotificacion(appdata=individuo.appdata)
    notif.titulo = 'Iniciar Proceso de supervisión Digital'
    notif.mensaje = 'Por Favor presione esta notificacion para iniciarlo.'
    notif.accion = 'BT'
    notif.save()#Al grabar el local, se envia automaticamente por firebase (signals)

def desactivar_tracking(individuo):
    AppNotificacion.objects.filter(appdata=individuo.appdata).delete()
    notif = AppNotificacion(appdata=individuo.appdata)
    notif.titulo = 'Finalizar Proceso de supervisión Digital'
    notif.mensaje = 'Por Favor presione esta notificacion para terminarlo.'
    notif.accion = 'ST'
    notif.save()#Al grabar el local, se envia automaticamente por firebase (signals)