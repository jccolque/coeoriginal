#Imports Django
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
#Imports del proyecto
from core.functions import paginador
from operadores.functions import obtener_operador
#Imports de la app
from .models import Tarea, Responsable, EventoTarea
from .forms import TareaForm, ResponsableForm, EventoTareaForm

# Create your views here.
@permission_required('operador.menu')
def menu(request):
    return render(request, 'menu_tareas.html', {})

#Manejo de Tareas
@permission_required('operador.ver_tarea')
def lista_tareas(request):
    tareas = Tarea.objects.all()
    tareas = tareas.order_by('subcomite').select_related('subcomite')
    tareas = paginador(request, tareas)
    return render(request, "lista_tareas.html", {'tareas': tareas, })

@permission_required('operador.ver_tarea')
def ver_tarea(request, tarea_id):
    tarea = Tarea.objects.get(pk=tarea_id)
    return render(request, "ver_tarea.html", {'tarea': tarea, })

@permission_required('operador.crear_tarea')
def crear_tarea(request):
    form = TareaForm()
    if request.method == "POST":
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save()
            #Creamos el primer responsable: El creador
            responsable = Responsable()
            responsable.tarea = tarea
            responsable.operador = obtener_operador(request)
            responsable.obligaciones = 'Creo la Tarea'
            responsable.save()
            #Creamos el evento de inicio
            evento = EventoTarea()
            evento.tarea = tarea
            evento.responsable = responsable
            evento.detalle = "Creacion de la Tarea"
            evento.save()
            return redirect('tareas:ver_tarea', tarea_id=tarea.id)
    return render(request, "extras/generic_form.html", {'titulo': "Crear Tarea", 'form': form, 'boton': "Crear", })

@permission_required('operador.crear_tarea')
def eliminar_tarea(request, tarea_id):
    tarea = Tarea.objects.get(pk=tarea_id)
    tarea.delete()
    return redirect('tareas:lista_tareas', )

#Responsable
@permission_required('operador.crear_tarea')
def agregar_responsable(request, tarea_id):
    tarea = Tarea.objects.get(pk=tarea_id)
    form = ResponsableForm(initial={'tarea': tarea, })
    if request.method == "POST":
        form = ResponsableForm(request.POST)
        if form.is_valid():
            responsable = form.save(commit=False)
            responsable.tarea = tarea
            responsable.save()
            return redirect('tareas:ver_tarea', tarea_id=tarea.id)
    return render(request, "extras/generic_form.html", {'titulo': "Agregar Responsable", 'form': form, 'boton': "Agregar", })

@permission_required('operador.crear_tarea')
def eliminar_responsable(request, responsable_id):
    responsable = Responsable.objects.get(pk=responsable_id)
    tarea = responsable.tarea
    responsable.delete()
    return redirect('tareas:ver_tarea', tarea_id=tarea.id)

#Eventos
@permission_required('operador.crear_tarea')
def agregar_evento(request, tarea_id):
    tarea = Tarea.objects.get(pk=tarea_id)
    form = EventoTareaForm(initial={'tarea': tarea, })
    if request.method == "POST":
        form = EventoTareaForm(request.POST, initial={'tarea': tarea, })
        if form.is_valid():
            evento = form.save(commit=False)
            evento.tarea = tarea
            evento.save()
            return redirect('tareas:ver_tarea', tarea_id=tarea.id)
    return render(request, "extras/generic_form.html", {'titulo': "Agregar Evento", 'form': form, 'boton': "Agregar", })

@permission_required('operador.crear_tarea')
def eliminar_evento(request, evento_id):
    evento = EventoTarea.objects.get(pk=evento_id)
    tarea = evento.tarea
    evento.delete()
    return redirect('tareas:ver_tarea', tarea_id=tarea.id)