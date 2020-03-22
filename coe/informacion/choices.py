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
    (9, 'Fuera del Territorio'),
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

TIPO_SEGUIMIENTO = (
    ('I', 'Inclusion al Sistema'),
    ('L', 'Llamada Telefonica'),
    ('M', 'Reporte Medico'),
    ('F', 'Fin del Seguimiento/Alta'),
)

TIPO_RELACION = (
    ('F', 'Familiar'),
    ('CE', 'Contacto Bajo Riesgo'),
    ('CA', 'Contacto Alto Riesgo'),
    ('O', 'Otro...'),
)

TIPO_ATRIBUTO = (
    ('PR', 'Poblacion de Riesgo/Comorbilidades'),
    ('DE', 'Denuncia Externa'),
    ('IP', 'Informado Por'),
    ('ER', 'Esperando Resultados'),
    ('VE', 'Vigilancia Epidemiologica'),
    ('AS', 'Es Agente de Salud'),
    ('PS', 'Es Personal de Seguridad'),
    ('PD', 'Se encuentra Presos/Detenidos'),
)

TIPO_SINTOMA = (
    ('DPR', 'Dificultad para Respirar'),
    ('DM', 'Dolor Muscular'),
    ('DRO', 'Dolor RetroOcular'),
    ('ART', 'Dolor de Articulaciones'),
    ('DC', 'Dolor de Cabeza'),
    ('DG', 'Dolor de Garganta'),
    ('DSV', 'Dolor parte Superior del Vientre'),
    ('FAT', 'Fatiga'),
    ('FIE', 'Fiebre'),
    ('HEP', 'Hemorragia Profusa'),
    ('IO', 'Inflamacion de los Ojos'),
    ('MAR', 'Mareos'),
    ('NAS', 'Nauseas'),
    ('PAL', 'Palidez'),
    ('PDA', 'Perdida de Apetito'),
    ('RCA', 'Ritmo Cardiaco Acelerado'),
    ('SAR', 'Sarpullido'),
    ('SRM', 'Sarpullido Rojo con Manchas en la Piel'),
    ('SN', 'Secrecion Nasal'),
    ('TOS', 'Tos'),
    ('VOM', 'Vomitos'),
)