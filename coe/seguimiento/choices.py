TIPO_SEGUIMIENTO = (
    ('I', 'Inclusion al Sistema'),
    ('A', 'Autodiagnostico'),
    ('IT', 'Inicio Tracking'),
    ('AT', 'Alerta Tracking'),
    ('FT', 'Finalizacion del Tracking'),
    ('DF', 'Domicilio Fuera de la Provincia'),
    ('PT', 'Pidio Test'),
    ('TA', 'Traslado a Aislamiento'),
    ('RC', 'Registro de Circulacion Temporal'),
    #Todos los usuarios
    ('L', 'Llamada Telefonica'),
    ('M', 'Reporte Medico'),
    ('C', 'Cronologia'),
    ('E', 'Epicrisis'),    
    ('TE', 'No Posee Telefono / Telefono Equivocado'),
    ('FS', 'Fin del Seguimiento/Alta'),
    #Solo usuarios con permiso: 
    ('ET', 'Esperando Resultados PCR'),
    ('CT', 'Confirmado por Test'),
    ('DT', 'Descartado por Test'),
)

def obtener_seguimientos(user):
    #Tipo de Seguimientos:
    sistema = ['I', 'A', 'IT', 'AT', 'FT', 'DF', 'PT', 'TA', 'RC']
    publicos = ['L', 'M', 'C', 'E', 'TE', 'FS']
    epidemiologia = ['ET', 'CT', 'DT']
    #Generamos seguimientos accesibles
    tipos = [t for t in TIPO_SEGUIMIENTO if t[0] in publicos]
    #Agregamos segun permisos:
    if user.has_perm('operadores.epidemiologia'):
        tipos += [t for t in TIPO_SEGUIMIENTO if t[0] in epidemiologia]
    if user.has_perm('operadores.sistemas'):
        tipos += [t for t in TIPO_SEGUIMIENTO if t[0] in sistema]
    return tipos

TIPO_VIGIA = (
    ('E', 'Vigilancia Epidemiologica'),
    ('M', 'Salud Mental'),
    ('T', 'Vigilancia de Transportistas'),
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