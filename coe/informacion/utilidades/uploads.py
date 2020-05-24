#CARGAS MASIVAS
@superuser_required
def upload_padron_individuos(request):
    form = ArchivoFormWithPass()
    if request.method == "POST":
        form = ArchivoFormWithPass(request.POST, request.FILES)
        if form.is_valid():
            #Eliminamos todos los objetos del padron
            Individuo.objects.filter(observaciones="PADRON").delete()
            #Generamos el archivo en la db
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            tarea = crear_progress_link("SUBIR_PADRON:"+str(timezone.now()))
            #Dividimos en fragmentos
            frag_size = 10000
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:#Procesamos todos menos el ultimo
                guardar_padron_individuos(segmento, archivo_id=archivo.id, queue=tarea)
            #Para que marque el archivo como terminado
            guardar_padron_individuos(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "CARGA MASIVA PADRON INDIVIDUOS", 'form': form, 'boton': "Subir", })

@superuser_required
def upload_padron_domicilios(request):
    form = ArchivoFormWithPass()
    if request.method == "POST":
        form = ArchivoFormWithPass(request.POST, request.FILES)
        if form.is_valid():
            #Eliminamos todos los objetos del padron
            Situacion.objects.filter(aclaracion="CARGA SAME").delete()
            Seguimiento.objects.filter(aclaracion="CARGA SAME").delete()
            Sintoma.objects.filter(aclaracion__icontains="CARGA SAME:").delete()
            Atributo.objects.filter(aclaracion__icontains="CARGA SAME:").delete()
            #Generamos el archivo en la db
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            tarea = crear_progress_link("SUBIR_PADRON:"+str(timezone.now()))
            #Dividimos en fragmentos
            frag_size = 10000
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:#Procesamos todos menos el ultimo
                guardar_padron_domicilios(segmento, archivo_id=archivo.id, queue=tarea)
            #Para que marque el archivo como terminado
            guardar_padron_domicilios(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "CARGA MASIVA PADRON DOMICILIOS", 'form': form, 'boton': "Subir", })

@permission_required('operadores.archivos')
def subir_same(request):
    form = ArchivoForm(initial={'tipo':5, 'nombre': str(timezone.now())[0:16]})
    if request.method == "POST":
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            lines = lines[1:]
            tarea = crear_progress_link("SUBIR_SAME:"+str(timezone.now()))
            frag_size = 25#Dividimos en fragmentos de 25
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:
                guardar_same(segmento, archivo_id=archivo.id, queue=tarea)
            guardar_same(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "CARGA MASIVA SAME", 'form': form, 'boton': "Subir", })

@superuser_required
def subir_epidemiologia(request):
    form = ArchivoFormWithPass(initial={'tipo':6, 'nombre': str(timezone.now())[0:16]})
    if request.method == "POST":
        form = ArchivoFormWithPass(request.POST, request.FILES)
        if form.is_valid():
            #Eliminamos registros previamente Cargados
            Domicilio.objects.filter(aclaracion="EPIDEMIOLOGIA").delete()
            Situacion.objects.filter(aclaracion="EPIDEMIOLOGIA").delete()
            Seguimiento.objects.filter(aclaracion="EPIDEMIOLOGIA").delete()
            Sintoma.objects.filter(aclaracion__icontains="EPIDEMIOLOGIA").delete()
            #Generamos archivo en la DB
            operador = obtener_operador(request)
            archivo = form.save(commit=False)
            archivo.operador = operador
            archivo.save()
            csv = archivo.archivo
            file_data = csv.read().decode("utf-8")
            lines = file_data.split("\n")
            lines = lines[1:]
            tarea = crear_progress_link("SUBIR_EPIDEMIOLOGIA:"+str(timezone.now()))
            frag_size = 100#Dividimos en fragmentos de 100
            segmentos = [lines[x:x+frag_size] for x in range(0, len(lines), frag_size)]
            for segmento in segmentos[0:-1]:
                guardar_epidemiologia(segmento, archivo_id=archivo.id, queue=tarea)
            guardar_epidemiologia(segmentos[-1], archivo_id=archivo.id, queue=tarea, ultimo=True)
            return redirect('informacion:ver_archivo', archivo_id=archivo.id)
    return render(request, "extras/generic_form.html", {'titulo': "CARGA MASIVA EPIDEMIOLOGIA", 'form': form, 'boton': "Subir", })