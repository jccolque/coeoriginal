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
    ('A', 'Aprobado'),
    ('B', 'Dado de Baja'),
)

COMBINACION_DNIxDIA = (
    ('0-0', 'Lunes Habilitada Terminacion: 0'),
    ('0-1', 'Lunes Habilitada Terminacion: 1'),
    ('0-2', 'Lunes Habilitada Terminacion: 2'),
    ('0-3', 'Lunes Habilitada Terminacion: 3'),
    ('0-4', 'Lunes Habilitada Terminacion: 4'),
    ('0-5', 'Lunes Habilitada Terminacion: 5'),
    ('0-6', 'Lunes Habilitada Terminacion: 6'),
    ('0-7', 'Lunes Habilitada Terminacion: 7'),
    ('0-8', 'Lunes Habilitada Terminacion: 8'),
    ('0-9', 'Lunes Habilitada Terminacion: 9'),
    ('1-0', 'Martes Habilitada Terminacion: 0'),
    ('1-1', 'Martes Habilitada Terminacion: 1'),
    ('1-2', 'Martes Habilitada Terminacion: 2'),
    ('1-3', 'Martes Habilitada Terminacion: 3'),
    ('1-4', 'Martes Habilitada Terminacion: 4'),
    ('1-5', 'Martes Habilitada Terminacion: 5'),
    ('1-6', 'Martes Habilitada Terminacion: 6'),
    ('1-7', 'Martes Habilitada Terminacion: 7'),
    ('1-8', 'Martes Habilitada Terminacion: 8'),
    ('1-9', 'Martes Habilitada Terminacion: 9'),
    ('2-0', 'Miercoles Habilitada Terminacion: 0'),
    ('2-1', 'Miercoles Habilitada Terminacion: 1'),
    ('2-2', 'Miercoles Habilitada Terminacion: 2'),
    ('2-3', 'Miercoles Habilitada Terminacion: 3'),
    ('2-4', 'Miercoles Habilitada Terminacion: 4'),
    ('2-5', 'Miercoles Habilitada Terminacion: 5'),
    ('2-6', 'Miercoles Habilitada Terminacion: 6'),
    ('2-7', 'Miercoles Habilitada Terminacion: 7'),
    ('2-8', 'Miercoles Habilitada Terminacion: 8'),
    ('2-9', 'Miercoles Habilitada Terminacion: 9'),
    ('3-0', 'Jueves Habilitada Terminacion: 0'),
    ('3-1', 'Jueves Habilitada Terminacion: 1'),
    ('3-2', 'Jueves Habilitada Terminacion: 2'),
    ('3-3', 'Jueves Habilitada Terminacion: 3'),
    ('3-4', 'Jueves Habilitada Terminacion: 4'),
    ('3-5', 'Jueves Habilitada Terminacion: 5'),
    ('3-6', 'Jueves Habilitada Terminacion: 6'),
    ('3-7', 'Jueves Habilitada Terminacion: 7'),
    ('3-8', 'Jueves Habilitada Terminacion: 8'),
    ('3-9', 'Jueves Habilitada Terminacion: 9'),
    ('4-0', 'Viernes Habilitada Terminacion: 0'),
    ('4-1', 'Viernes Habilitada Terminacion: 1'),
    ('4-2', 'Viernes Habilitada Terminacion: 2'),
    ('4-3', 'Viernes Habilitada Terminacion: 3'),
    ('4-4', 'Viernes Habilitada Terminacion: 4'),
    ('4-5', 'Viernes Habilitada Terminacion: 5'),
    ('4-6', 'Viernes Habilitada Terminacion: 6'),
    ('4-7', 'Viernes Habilitada Terminacion: 7'),
    ('4-8', 'Viernes Habilitada Terminacion: 8'),
    ('4-9', 'Viernes Habilitada Terminacion: 9'),
    ('5-0', 'Sabado Habilitada Terminacion: 0'),
    ('5-1', 'Sabado Habilitada Terminacion: 1'),
    ('5-2', 'Sabado Habilitada Terminacion: 2'),
    ('5-3', 'Sabado Habilitada Terminacion: 3'),
    ('5-4', 'Sabado Habilitada Terminacion: 4'),
    ('5-5', 'Sabado Habilitada Terminacion: 5'),
    ('5-6', 'Sabado Habilitada Terminacion: 6'),
    ('5-7', 'Sabado Habilitada Terminacion: 7'),
    ('5-8', 'Sabado Habilitada Terminacion: 8'),
    ('5-9', 'Sabado Habilitada Terminacion: 9'),
    ('6-0', 'Domingo Habilitada Terminacion: 0'),
    ('6-1', 'Domingo Habilitada Terminacion: 1'),
    ('6-2', 'Domingo Habilitada Terminacion: 2'),
    ('6-3', 'Domingo Habilitada Terminacion: 3'),
    ('6-4', 'Domingo Habilitada Terminacion: 4'),
    ('6-5', 'Domingo Habilitada Terminacion: 5'),
    ('6-6', 'Domingo Habilitada Terminacion: 6'),
    ('6-7', 'Domingo Habilitada Terminacion: 7'),
    ('6-8', 'Domingo Habilitada Terminacion: 8'),
    ('6-9', 'Domingo Habilitada Terminacion: 9'),
)
