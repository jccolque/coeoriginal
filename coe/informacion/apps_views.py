#Imports Django
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
#Imports extras
from fcm_django.models import FCMDevice
#Imports de la app
from .app_forms import SendNotificationForm, AppNotificationForm

#NUESTRAS VISTAS:
def download_app(request):
    return redirect('https://play.google.com/store/apps/details?id=com.ga.covidjujuy_app')

#Enviar notificaciones
@staff_member_required
def enviar_notificacion(request):
    form = SendNotificationForm()
    if request.method == 'POST':
        form = SendNotificationForm(request.POST)
        if form.is_valid:
            try:
                device = FCMDevice.objects.get(pk=request.POST['dispositivo'])
                device.send_message(
                    title= request.POST['titulo'],
                    body= request.POST['texto'],
                    color= request.POST['color'],
                    #icon=request.POST['icono'], data={"test": "test"}
                )
                return render(request, "extras/resultado.html", {"texto": "Se envio el mensaje deseado."})
            except Exception as e:
                return render(request, 'extras/error.html', {
                    'titulo': 'No se pudo enviar el mensaje',
                    'error': str(e),
                })
    return render(request, "extras/generic_form.html", {'titulo': "Enviar Notificacion via Push", 'form': form, 'boton': "Enviar", })

@staff_member_required
def guardar_notificacion(request):
    form = AppNotificationForm()
    if request.method == 'POST':
        form = AppNotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "extras/resultado.html", {"texto": "Se Guardo el mensaje deseado."})
    return render(request, "extras/generic_form.html", {'titulo': "Guardar Notificacion Local", 'form': form, 'boton': "Guardar", })