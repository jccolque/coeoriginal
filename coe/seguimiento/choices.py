TIPO_SEGUIMIENTO = (
    ('I', 'Inclusion al Sistema'),
    ('A', 'Autodiagnostico'),

    ('IT', 'Inicio Tracking'),
    ('AT', 'Alerta Tracking'),
    ('FT', 'Finalizacion del Tracking'),
    
    ('DF', 'Domicilio Fuera de la Provincia'),
    ('L', 'Llamada Telefonica'),
    ('M', 'Reporte Medico'),
    ('C', 'Cronologia'),
    ('E', 'Epicrisis'),
    
    ('TA', 'Traslado a Aislamiento'),
    ('RC', 'Registro de Circulacion Temporal'),
    ('TE', 'No Posee Telefono / Telefono Equivocado'),
    ('FS', 'Fin del Seguimiento/Alta'),

    ('PT', 'Pidio Test'),
    ('ET', 'Esperando Resultados PCR'),
    ('CT', 'Confirmado por Test'),
    ('DT', 'Descartado por Test'),
)

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