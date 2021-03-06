"""coe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#Imports de Django
from django.conf.urls import url
from django.urls import path, include

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

from django.conf import settings
#Imports Extras
import debug_toolbar

#Path
urlpatterns = [
    path('admin/', admin.site.urls),
    #Admin-User Paths
    url(r'^login/$', auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    #Extras
    url(r'^tinymce/', include('tinymce.urls')),
    #Debug:
    path('__debug__/', include(debug_toolbar.urls)),
    #Apps:
    path('', include('core.urls')),
    path('consultas/', include('consultas.urls')),
    path('georef/', include('georef.urls')),
    path('noticias/', include('noticias.urls')),
    path('operadores/', include('operadores.urls')),
    path('actas/', include('actas.urls')),
    path('tareas/', include('tareas.urls')),
    path('inventario/', include('inventario.urls')),
    path('informacion/', include('informacion.urls')),
    path('seguimiento/', include('seguimiento.urls')),
    path('geotracking/', include('geotracking.urls')),
    path('permisos/', include('permisos.urls')),
    path('graficos/', include('graficos.urls')),
    path('documentos/', include('documentos.urls')),
    path('inscripciones/', include('inscripciones.urls')),
    path('background/', include('background.urls')),
    path('tablero/', include('tablero.urls')),
    #APIS:
    path('api_refs/', include('wservices.urls')),
    path('ide/', include('geotracking.ide_urls')),
    path('covid19/', include('app.urls')),
    #Manejo de Archivos Privados:
    #path('archivos/', include('operadores.file_urls')),#Lo hacemos desde ahi por que depende de permisos
]
#Agregamos destinos de Archivos Estaticos
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
