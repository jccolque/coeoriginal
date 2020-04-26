COLOR_RESTRICCION = (
    ('B', 'Blanco (Normalidad)'),
    ('V', 'Verde (Minima)'),
    ('A', 'Amarillo (Intermedia)'),
    ('R', 'Rojo (Maxima)'),
    ('D', 'Permisos Digitales Desactivados'),
)

GRUPOS_PERMITIDOS = (
    (0, 'No se Autoriza a Nadie'),
    (1, 'Todos los DNI diariamente'),
    (2, 'Division por Pares e Impares'),
    (3, 'Tres Grupos: 1,2,3 - 4,5,6 - 7,8,9,0'),
    (5, 'Cinco Grupos: 1,2 - 3,4 - 5,6 - 7,8 - 9,0'),
)

TIPO_PERMISO = (
    ('C', 'Compras de Primera Necesidad'),
    ('F', 'Compras de Farmacia'),
    ('B', 'Turno Bancario'),
    ('R', 'Responsable de Personas a Cargo'),
    ('P', 'Permiso Permanente'),
)

TIPO_INGRESO = (
    ('P', 'Particular en Vehiculo Propio'),
    ('C', 'Colectivo (Carga la Empresa)'),
    ('A', 'Aereo (Carga la Empresa)'),
)

ESTADO_INGRESO = (
    ('C', 'Cargando Pedido'),
    ('E', 'Esperando Aprobacion'),
    ('B', 'Dado de Baja'),
    ('A', 'Aprobado'),
)