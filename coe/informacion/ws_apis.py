#Imports Django
from django.utils import timezone
from django.http import JsonResponse
#Imports de la app
from .models import Situacion

#Creamos nuestros webservices
def ws_situaciones(request, fecha=None):
    estados = {}
    conductas = {}
    #Traemos todas las situaciones
    situaciones = Situacion.objects.all()
    #Si filtra por fecha
    if fecha:#Filtramos \_o_/
        situaciones = situaciones.objects.get(fecha__date=fecha)
    #Genermaos listado por conductas
    for s in situaciones:
        #Contamos estados
        if s.get_estado_display() in estados:
            estados[s.get_estado_display()] += 1
        else:
            estados[s.get_estado_display()] = 1
        #Contamos conductas
        if s.get_conducta_display() in conductas:
            conductas[s.get_conducta_display()] += 1
        else:
            conductas[s.get_conducta_display()] = 1
    #Le cambiamos los valores:
    return JsonResponse(
        {
            "action": "situaciones",
            "fecha": timezone.now(),
            "estados": estados,
            "conductas": conductas,
        },
        safe=False
    )
