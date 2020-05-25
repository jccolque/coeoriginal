#Choice Fields
TIPO_REFERENCIA = (
    ('N', 'Ninguna'),
    ('CFR', 'Con Factores de Riesgo'),
    ('H', 'Hacinamiento'),
    ('EC', 'Enfermedad Crónica'),
    ('O', 'Otro'),   
)

TIPO_ORGANIZACION = (
    ('ONG', 'ONG'),
    ('SDO', 'SINDICATO'),
    ('CI', 'COMUNIDAD INDIGENA'),
    ('ASC', 'ASOCIACION'),
    ('O', 'OTRO'),
)

TIPO_CONFIRMA = (
    ('NO', 'NO'),
    ('SI', 'SI'),
)

ESTADO_PEDIDO = (
    ('C', 'Cargando Pedido'),
    ('E', 'Pedido Cargado'),    
    ('A', 'Aprobado'),
    ('B', 'Dado de Baja'),
)