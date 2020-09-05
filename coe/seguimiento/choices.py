TIPO_SEGUIMIENTO = (
    #Todos los usuarios
    ('L', 'Llamada Telefonica'),
    ('T', 'Intervencion en Territorio'),
    #('EM', 'Requiere Seguimiento URGENTE medico'),
    ('M', 'Reporte Medico'),
    ('C', 'Cronologia'),
    ('E', 'Epicrisis'),
    ('IR', 'Individuo Sospechoso: Evaluar'),
    ('TE', 'No Posee Telefono / Telefono Equivocado'),
    ('PT', 'Pedido de Test'),
    ('FS', 'Fin del Seguimiento/Alta'),
    ('FA', 'Fallecido'),
    #Solo usuarios con permiso:
    ('ET', 'Esperando Resultados PCR'),
    ('CT', 'Confirmado por Test'),
    ('DT', 'Descartado por Test'),
    ('AP', 'Alta de Positivo por PCR'),
    #Sistema
    ('I', 'Inclusion al Sistema'),
    ('A', 'Autodiagnostico'),
    ('AI', 'Actualizacion de Individuo'),
    ('IT', 'Inicio Tracking'),
    ('AT', 'Alerta Tracking'),
    ('FT', 'Finalizacion del Tracking'),
    ('DF', 'Domicilio Fuera de la Provincia'),
    ('TA', 'Traslado a Aislamiento'),
    ('RC', 'Registro de Circulacion Temporal'),
)

def obtener_seguimientos(user):
    #Tipo de Seguimientos:
    sistema = ['I', 'A', 'IT', 'AT', 'FT', 'DF', 'TA', 'RC']
    publicos = ['L', 'T', 'M', 'C', 'E', 'IR', 'TE','FS', 'PT', 'FA']#, 'EM'
    epidemiologia = ['ET', 'CT', 'DT', 'AP']
    #Generamos seguimientos publicos
    tipos = [t for t in TIPO_SEGUIMIENTO if t[0] in publicos]
    #Agregamos segun permisos:
    if user.has_perm('operadores.epidemiologia'):
        tipos += [t for t in TIPO_SEGUIMIENTO if t[0] in epidemiologia]
    if user.has_perm('operadores.sistemas'):
        tipos += [t for t in TIPO_SEGUIMIENTO if t[0] in sistema]
    return tipos

TIPO_VIGIA = (
    ('VE', 'Vigilancia Epidemiologica'),
    ('VM', 'Vigilancia Salud Mental'),
    ('AP', 'Atencion Psiquiatrica'),
    ('ST', 'Vigilancia Medica'),
    ('VD', 'Vigilancia de Adultos Mayores'),
    ('VT', 'Vigilancia de Circulacion Temporal'),
    ('EM', 'Emergencia Medica - URGENTE'),
)

ESTADO_OPERATIVO = (
    ('C', 'Creado'),
    ('I', 'Inicializado'),
    ('F', 'Finalizado'),
    ('E', 'Eliminado'),
)

ESTADO_RESULTADO = (
    ('E', 'Esperando Resultado'),
    ('P', 'Positivo'),
    ('N', 'Negativo'),
)

TIPO_TURNO = (
    ('M', 'MANIANA'),
    ('T', 'TARDE'),
    ('N', 'NOCHE'),
)

#CONDICIONES AMBIENTALES:
NIVEL_CONTENCION = (
    (0, 'Convive con personas Adultas y Responsables'),
    (5, 'Posee Familiares que lo visitan regularmente'),
    (10, 'Posee Familiares que pueden auxiliarlo en Emergencias'),
    (15, 'Tiene Vecinos que lo contienen'),
    (30, 'No tiene Contencion de Ningun Tipo'),
)

NIVEL_ALIMENTOS = (
    (0, 'No tiene Problemas para conseguir lo que necesite'),
    (5, 'Esporadicamente le envian Mercaderia'),
    (20, 'Acceso minimo a elementos indispensables'),
    (30, 'Carece completamente de elementos basicos'),
)

NIVEL_MEDICACION = (
    (0, 'No requiere medicamentos'),
    (2, 'No tiene Problemas para conseguir sus medicamentos'),
    (25, 'Recibe irregularmente medicacion necesaria'),
    (30, 'Dificultad para recibir Medicacion Esencial'),
)
#Muestreo
ESTADO_TIPO = (
    ('EE', 'EN ESPERA'),
    ('EP', 'EN PROCESO'),
    ('F', 'FINALIZADO'),
)

TIPO_PRIORIDAD = (
    ('SP', 'SIN PRIORIDAD'),
    ('V', 'VERDE'),
    ('A', 'AMARILLO'),
    ('R', 'ROJO'),
)

TIPO_RESULTADO = (
    ('SR', 'SIN RESULTADO'),
    ('N', 'NEGATIVO PARA CORONAVIRUS'),
    ('P', 'POSITIVO PARA CORONAVIRUS'),
)