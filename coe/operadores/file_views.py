#Imports de Python
#Imports Django
from django.views.static import serve
from django.contrib.auth.decorators import permission_required
#Imports extras
#Import del proyecto
from coe.settings import MEDIA_ROOT
#Imports de la app

# Create your views here.
def entregar_file(request, filename):
    return serve(request, filename, MEDIA_ROOT)

@permission_required('operadores.menu_documentos')
def ver_documento(request, filename):
    return entregar_file(request, 'documentos/'+filename) 

@permission_required('operadores.menu_informacion')
def ver_archivo(request, filename):
    return entregar_file(request, 'informacion/archivos/'+filename) 

@permission_required('operadores.individuos')
def ver_foto_individuo(request, filename):
    return entregar_file(request, 'informacion/individuos/'+filename) 

@permission_required('operadores.individuos')
def ver_doc_individuo(request, filename):
    return entregar_file(request, 'informacion/individuo/documentos/'+filename) 

@permission_required('operadores.menu_operadores')
def ver_operador(request, filename):
    return entregar_file(request, 'operadores/'+filename) 

@permission_required('operadores.menu_inscripciones')
def ver_dni_inscripto(request, filename):
    return entregar_file(request, 'inscripciones/dni/'+filename) 

@permission_required('operadores.menu_inscripciones')
def ver_titulo_inscripto(request, filename):
    return entregar_file(request, 'inscripciones/titulo/'+filename) 