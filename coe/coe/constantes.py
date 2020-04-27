#Imports Python
from datetime import date, datetime, time

#Definimos constantes
LAST_DATE = date(9999, 12, 30)
LAST_DATETIME = datetime(9999, 12, 30, 23, 59)
DIAS_CUARENTENA = 14

#Horarios de Actividad
TIME_INICIO = time(8, 0, 0)
TIME_FIN = time(20, 0, 0)

#Faltantes
NOMAIL = 'sinemail@nomail.com'
NODOM = 'SINDOMICILIO'
NOTEL = 'SINTELEFONO'
NOIMAGE = '/static/img/subir_foto.png'

#GeoPosiciones
DISTANCIA_MAXIMA = 350000#300km en Metros
CENTRO_LATITUD = -24.2363472
CENTRO_LONGITUD = -64.8809494