# COE

Sistema de apoyo al Comite Operativo de Emergencias.

Para poder probar este proyecto solo deben Instalar:
- Python3.5+

Correr en la consola de su sistema operativo (Puede requerir permisos de administrador):
- pip install -r requeriments.txt   //Instala dependencias
- python3 manage.py makemigrations  //Prepara la creacion de la base de datos
- python3 manage.py migrate         //Crea la base de datos
- python3 manage.py createsuperuser //Crea usuario admin del sistema
- python3 manage.py runserver       //Lanza el servidor

Podran accederlo:
- Home: http://localhost:8000
- Admin: http://localhost:8000/admin
- 
#Generar PDF

Se deben instalar las librerías:
`pip install reportlab`

`pip install PyPDF2`

Se debe hacer el control de fechas; al pasar 14 días + 8 horas se debe dar de alta al que está en cuarentena.