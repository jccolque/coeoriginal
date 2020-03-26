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
    (5, 'Carga Masiva Same'),
    (6, 'Carga Masiva Epidemiologia'),
    (7, 'Carga Masiva Padron'),
)

TIPO_VEHICULO = (
    (1, 'Particular'),
    (2, 'Colectivo'),
    (3, 'Traffic'),
    (4, 'Comercial Pequeño'),
    (5, 'Avion'),
)

TIPO_ESTADO = (
    (1, 'Asintomatico'),
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
    ('DP', 'Dolor de Pecho'),
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
    ('ESC', 'Escalofrios')
)

TIPO_PERMISO = (
    ('L', 'Autoridades/Funcionarios Publicos'),
    ('S', 'Trabajador de la Salud/Seguridad'),
    ('T', 'Trabajador de Industria Estrategica'),
    ('A', 'Trabajador de Abastecimiento'),
    ('C', 'Salida Temporal por Compras de Primera Necesidad'),
    ('F', 'Salida Temporal por Compras de Farmacia'),
    ('P', 'Salida Temporal por Personas a Cargo'),
)

TIPO_TRIAJE = (
    ('V', 'Verde'),
    ('A', 'Amarillo'),
    ('R', 'Rojo'),
)