#Imports de python
import re
import traceback
#Imports django
from django.http import JsonResponse
from django.db.models.deletion import Collector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#Imports de la app
from .apps import CoreConfig

#Funciones para asignar a las app.configs    
def agregar_menu(app):
    CoreConfig.ADMIN_MENU += [(app.name.capitalize() , app.name)]

def paginador(request, queryset):
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 1000)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

def delete_tags(texto):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', texto)
  return cleantext

def date2str(fecha):
    return str(fecha)[8:10] + '/' + str(fecha)[5:7]

def is_related(instance):
    collector = Collector(using="default")
    collector.collect([instance])
    if collector.dependencies:
        return True

def json_error(error, vista, logger=None):
    if logger:
        logger.info("Falla: "+str(error))
    return JsonResponse(
            {
                "accion": vista,
                "realizado": False,
                "error": str(error),
                "error_contexto": str(error.__context__),
                "error_traceback": str(traceback.format_exc()),
            },
            safe=False,
            status=400,
        )