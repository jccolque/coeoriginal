TIPO_SEGUIMIENTO = (
    ('I', 'Inclusion al Sistema'),
    ('A', 'Autodiagnostico'),
    ('AI', 'Actualizacion de Individuo'),
    ('IT', 'Inicio Tracking'),
    ('AT', 'Alerta Tracking'),
    ('FT', 'Finalizacion del Tracking'),
    ('DF', 'Domicilio Fuera de la Provincia'),
    ('TA', 'Traslado a Aislamiento'),
    ('RC', 'Registro de Circulacion Temporal'),
    #Todos los usuarios
    ('L', 'Llamada Telefonica'),
    ('EM', 'Requiere Seguimiento URGENTE medico'),
    ('M', 'Reporte Medico'),
    ('C', 'Cronologia'),
    ('E', 'Epicrisis'),
    ('IR', 'Individuo Sospechoso: Evaluar'),
    ('ET', 'Esperando Resultados PCR'),
    ('TE', 'No Posee Telefono / Telefono Equivocado'),
    ('PT', 'Pedido de Test'),
    ('FS', 'Fin del Seguimiento/Alta'),
    ('FA', 'Fallecido'),
    #Solo usuarios con permiso: 
    ('CT', 'Confirmado por Test'),
    ('DT', 'Descartado por Test'),
    ('AP', 'Alta de Positivo por PCR'),
)

def obtener_seguimientos(user):
    #Tipo de Seguimientos:
    sistema = ['I', 'A', 'IT', 'AT', 'FT', 'DF', 'TA', 'RC']
    publicos = ['L', 'EM', 'M', 'C', 'E', 'IR', 'ET', 'TE','FS', 'PT', 'FA']
    epidemiologia = ['CT', 'DT', 'AP']
    #Generamos seguimientos accesibles
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
    ('VD', 'Vigilancia de Adultos Mayores'),
    ('ST', 'Vigilancia Medica'),
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
    (10, 'Acceso minimo a elementos indispensables'),
    (30, 'Carece de elementos basicos'),
)

NIVEL_MEDICACION = (
    (0, 'No requiere medicamentos'),
    (2, 'No tiene Problemas para conseguir sus medicamentos'),
    (10, 'Recibe irregularmente medicacion necesaria'),
    (30, 'Dificultad para recibir Medicacion Vital'),
)