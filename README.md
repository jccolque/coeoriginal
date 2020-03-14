# coronavirus

Sistema de apoyo al Comite Operativo de Emergencias por Coronavirus.

Para poder probar este proyecto solo deben Instalar:
- Python3+

Correr en la consola de su sistema operativo (Puede requerir permisos de administrador):
- pip install -r requeriments.txt   //Instala dependencias
- python3 manage.py makemigrations  //Prepara la creacion de la base de datos
- python3 manage.py migrate         //Crea la base de datos
- python3 manage.py createsuruser   //Crea usuario admin del sistema
- python3 manage.py runserver       //Lanza el servidor

Podran accederlo:
- Home: http://localhost:8000
- Admin: http://localhost:8000/admin