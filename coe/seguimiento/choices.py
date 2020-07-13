TIPO_SEGUIMIENTO = (
    ('I', 'Inclusion al Sistema'),
    ('A', 'Autodiagnostico'),
    ('IT', 'Inicio Tracking'),
    ('AT', 'Alerta Tracking'),
    ('FT', 'Finalizacion del Tracking'),
    ('DF', 'Domicilio Fuera de la Provincia'),
    ('TA', 'Traslado a Aislamiento'),
    ('RC', 'Registro de Circulacion Temporal'),
    ('PT', 'Pidio Test'),
    #Todos los usuarios
    ('L', 'Llamada Telefonica'),
    ('M', 'Reporte Medico'),
    ('C', 'Cronologia'),
    ('E', 'Epicrisis'),
    ('ET', 'Esperando Resultados PCR'),
    ('TE', 'No Posee Telefono / Telefono Equivocado'),
    ('FS', 'Fin del Seguimiento/Alta'),
    #Solo usuarios con permiso: 
    ('CT', 'Confirmado por Test'),
    ('DT', 'Descartado por Test'),
)

def obtener_seguimientos(user):
    #Tipo de Seguimientos:
    sistema = ['I', 'A', 'IT', 'AT', 'FT', 'DF', 'TA', 'RC', 'PT']
    publicos = ['L', 'M', 'C', 'E', 'TE', 'ET', 'FS']
    epidemiologia = ['CT', 'DT']
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
    ('ST', 'Seguimiento Clinico de TeleSalud'),
    ('VT', 'Vigilancia de Circulacion Temporal'),
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