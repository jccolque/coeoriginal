TIPO_GEOPOS = (
    ('MS', 'Manual desde Sistema'),
    ('AD', 'AutoDiagnostico'),
    ('ST', 'Inicio de Tracking/Base'),
    ('PC', 'Punto de Control'),#Lugar de referencia
    ('RG', 'Reporte de GeoPosicion'),
    ('CG', 'Control GeoPosicion'),
)

TIPO_ALERTA = (
    ('SA', 'Sin Alerta'),
    ('DA', 'Distancia de Alerta'),
    ('DC', 'Distancia Critica'),
    ('FG', 'Falta de GeoTracking'),
    ('SC', 'Sin Punto de Control Asignado'),
    ('SM', 'Sin Movimiento'),
    ('FP', 'Falta Permiso'),
)