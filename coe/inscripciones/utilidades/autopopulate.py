from inscripciones.models import Area, Tarea

def cargar_tareas():
    area = Area.objects.get_or_create(nombre="ADMINISTRACION", orden=1)[0]
    tarea = Tarea.objects.get_or_create(area=area, nombre="Recepción", orden=1)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Registro y carga de datos", orden=2)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Administración, archivo y clasificación de información pertinente referida a la emergencia para la cual se ha inscripto", orden=3)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Administración de personas y Turnos", orden=4)
    area = Area.objects.get_or_create(nombre="ATENCIÓN DE LA SALUD", orden=2)[0]
    tarea = Tarea.objects.get_or_create(area=area, nombre="Primeros auxilios emocionales y psicológicos", orden=1)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Detección de factores de riesgo", orden=2)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Consejos para la Higiene personal y de Hábitat de ancianos, enfermos y minusválidos", orden=3)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Asistencia para realizar las caminatas dentro de los espacios permitidos y ante la imposibilidad de hacerlo", orden=4)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Elaboración de comidas y dietas específicas para determinados grupos de riesgo (diabéticos, hipertensos, obesos, etc.)", orden=5)
    area = Area.objects.get_or_create(nombre="OPERATIVA", orden=3)[0]
    tarea = Tarea.objects.get_or_create(area=area, nombre="Conducir, cargar combustible y mantenimiento de los vehículos afectados al Programa", orden=1)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Distribuir las personas que forman parte del Programa, los elementos, insumos o alimentos que le sea requerido realizar a los diferentes puntos y lugares.", orden=2)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Actividad de asistencia a los respondedores (Salud, Seguridad etc.)", orden=3)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Operación de equipos de comunicación", orden=4)
    area = Area.objects.get_or_create(nombre="LOGÍSTICA", orden=4)[0]
    tarea = Tarea.objects.get_or_create(area=area, nombre="Recepción, clasificación, acopio y empaque de insumos, alimentos y elementos necesarios para distribución en las actividades de respuesta a las áreas e instituciones que estén involucradas en el sistema de emergencia provincial", orden=1)
    area = Area.objects.get_or_create(nombre="SEGURIDAD", orden=5)[0]
    tarea = Tarea.objects.get_or_create(area=area, nombre="Auxiliar en las tareas de ordenamiento y seguridad comunitaria.", orden=1)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Auxiliar en materia de tránsito o policial, acompañamiento para el control de los accesos a la localidad, auxiliar de las actividades que realice el personal policial en cumplimiento de sus funciones.", orden=2)
    area = Area.objects.get_or_create(nombre="EDUCACIÓN Y CULTURA", orden=6)[0]
    tarea = Tarea.objects.get_or_create(area=area, nombre="Lectura virtual de libros de recreación y acompañamiento mediante juegos de mesa tales como ajedrez, dama, etc. Y toda otra forma de recreación como juegos de ingenio, crucigramas, sopas de letra, etc.", orden=1)
    tarea = Tarea.objects.get_or_create(area=area, nombre="Actividades educativas de sensibilización, cuidado, protección, recreativas y de contención para adultos mayores afectados.", orden=2)