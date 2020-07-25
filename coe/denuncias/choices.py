TIPO_LLAMADA = (
    ('CT', 'Consulta Tecnica'),
    ('CM', 'Consulta Medica'),
)

TIPO_TELEFONISTA = (
    ('MX', 'Llamadas, Denuncias y Consultas'),
    ('DE', 'Operador Denuncias'),
    ('ES', 'Operador Consultas'),
    ('LL', 'Operador Telefonico'),
)

TIPO_DENUNCIA = (
    ('NC', 'No respeta la cuarentena'),
    ('NF', 'Negocio en Falta'),
    ('PC', 'No respeta Precios Maximos'),
    ('SB', 'Sin Barbijo en Via Publica'),
    ('RM', 'Reunion Ilegal de Varios individuos'),
)

ESTADO_DENUNCIA = (
    ('IN', 'Enviada desde Dispositivo'),
    ('EL', 'Elevada a las autoridades pertinentes'),
    ('RE', 'Resuelta'),
    ('BA', 'Dada de Baja'),
)