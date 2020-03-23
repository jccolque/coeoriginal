#Imports Django
from django.shortcuts import render

#Imports de la appa
from .models import Progress_Links

# Create your views here.
def lista_background(request):
    tasks = Progress_Links.objects.all()
    return render(request, 'lista_background.html', {
        'tasks': tasks,
        "refresh": True 
        }
    )

def ver_background(request, task_id):
    task = Progress_Links.objects.get(pk=task_id)
    return render(request, 'ver_background.html', {
        "task": task,
        "refresh": True }
    )