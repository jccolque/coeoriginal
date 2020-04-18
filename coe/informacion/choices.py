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
    (7, 'Carga Masiva Padron Individuos'),
    (7, 'Carga Masiva Padron Domicilios'),
)

TIPO_VEHICULO = (
    (1, 'Transporte Sanitario'),
    (2, 'Particular'),
    (3, 'Colectivo'),
    (4, 'Traffic'),
    (5, 'Comercial Pequeño'),
    (6, 'Avion'),
)

TIPO_ESTADO = (
    (11, 'Asintomatico'),
    (10, 'Sano'),
    (31, 'Contacto Bajo Riesgo'),
    (32, 'Contacto Alto Riesgo'),
    (40, 'Sospechoso'),
    (50, 'Confirmado'),
    (2, 'Curado'),
    (1, 'Fallecido'),
    (0, 'Fuera del Territorio'),
)

TIPO_CONDUCTA = (
    ('A', 'Nada'),
    ('B', 'Evaluar'),
    ('C', 'Cuarentena Voluntaria'),
    ('D', 'Cuarentena Obligatoria'),
    ('E', 'Aislamiento'),
    ('F', 'En Morgue'),
    ('G', 'Cremado'),
    ('H', 'Enterrado'),
)

TIPO_SEGUIMIENTO = (
    ('I', 'Inclusion al Sistema'),
    ('L', 'Llamada Telefonica'),
    ('M', 'Reporte Medico'),
    ('C', 'Cronologia'),
    ('E', 'Epicrisis'),
    ('ET', 'Esperando Resultados'),
    ('CT', 'Confirmado por Test'),
    ('DT', 'Descartado por Test'),
    ('A', 'Autodiagnostico'),
    ('FS', 'Fin del Seguimiento/Alta'),
    ('IT', 'Inicio Tracking'),
    ('AT', 'Alerta Tracking'),
    ('FT', 'Baja Tracking'),
    ('TA', 'Traslado a Aislamiento'),
)

TIPO_RELACION = (
    ('F', 'Familiar'),
    ('CE', 'Contacto Bajo Riesgo'),
    ('CA', 'Contacto Alto Riesgo'),
    ('MD', 'Mismo Domicilio'),
    ('O', 'Otro...'),
)

TIPO_ATRIBUTO = (
    ('PR', 'Poblacion de Riesgo/Comorbilidades'),
    ('DE', 'Denuncia Externa'),
    ('IP', 'Informado Por'),
    ('VE', 'Vigilancia Epidemiologica'),
    ('AS', 'Es Agente de Salud'),
    ('PS', 'Es Personal de Seguridad'),
    ('FP', 'Es Funcionario Publico'),
    ('TE', 'Es Trabajador de Empresa Estrategica'),
    ('PD', 'Se encuentra Presos/Detenidos'),
    ('CE', 'Visito Pais de Riesgo/Contacto con Extranjeros'),
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

TIPO_DOCUMENTO = (
    ('HM', 'Historia Medica'),
    ('RG', 'Radiografia'),
    ('EC', 'Electrocardiograma'),
    ('AS', 'Analisis de Sangre'),
    ('AO', 'Analisis de Orina'),
    ('LB', 'Laboratorio'),
    ('OT', 'Otros'),
)