#Imports de Python
#Imports de Django
#Imports de la app
from documentos.models import Documento

#Definimos nuestras funciones
def ver_publicadas(limit=None):
    versiones = []
    documentos = Documento.objects.filter(publico=True)
    documentos = documentos.prefetch_related('versiones')
    for doc in documentos:
        version = doc.ultima_version()
        if version:
            if hasattr(version, 'archivo'):
                versiones.append(version)
    versiones.sort(key=lambda x: x.fecha, reverse=True)
    if limit:
        versiones = versiones[0:limit]
    return versiones
    