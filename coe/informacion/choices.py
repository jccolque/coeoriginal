#Choice Fields
TIPO_IMPORTANCIA = (
    (0, 'Nula'),
    (1, 'Baja'),
    (2, 'Intermedia'),
    (3, 'Alta'),
)

TIPO_ARCHIVO = (
    (1, 'Acta Pasajeros'),
    (2, 'Informe Externo'),
    (3, 'Informe Particular'),
    (4, 'Denuncia'),
)

TIPO_VEHICULO = (
    (1, 'Particular'),
    (2, 'Colectivo'),
    (3, 'Traffic'),
    (4, 'Comercial Pequeño'),
    (5, 'Avion'),
)

TIPO_ESTADO = (
    (1, 'Dudoso'),
    (2, 'Sano'),
    (31, 'Contacto Bajo Riesgo'),
    (32, 'Contacto Alto Riesgo'),
    (4, 'Sospechoso'),
    (5, 'Confirmado'),
    (6, 'Curado'),
    (71, 'Fallecido'),
)

TIPO_CONDUCTA = (
    ('A', 'Nada'),
    ('B', 'Evaluar'),
    ('C', 'Cuarentena Voluntaria'),
    ('D', 'Cuarentena Obligatoria'),
    ('E', 'Aislado'),

    ('F', 'En Morgue'),
    ('G', 'Cremado'),
    ('H', 'Enterrado'),
)

TIPO_RELACION = (
    ('F', 'Familiar'),
    ('CE', 'Contacto Bajo Riesgo'),
    ('CA', 'Contacto Alto Riesgo'),
    ('O', 'Otro...'),
)