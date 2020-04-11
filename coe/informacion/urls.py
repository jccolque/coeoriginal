#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
from . import autocomplete

#Definimos paths de la app
app_name = 'informacion'
urlpatterns = [
    #Publico
    path('buscar/', views.buscar_permiso, name='buscar_permiso'),
    path('permiso/<int:individuo_id>/<int:num_doc>/', views.pedir_permiso, name='pedir_permiso'),
    path('completar/datos/<int:individuo_id>', views.completar_datos, name='completar_datos'),
    path('subir/foto/<int:individuo_id>', views.subir_foto, name='subir_foto'),
    #Administrador
    path('', views.menu, name='menu'),
    #Archivos
    path('lista/archivos/pendientes', views.archivos_pendientes, name='archivos_pendientes'),
    path('lista/archivos/procesados/<int:procesado>', views.archivos_pendientes, name='archivos_procesados'),
    path('ver_archivo/<int:archivo_id>', views.ver_archivo, name='ver_archivo'),
    path('subir/archivos', views.upload_archivos, name='subir_archivos'),
    path('subir/same', views.subir_same, name='subir_same'),
    path('subir/epidemiologia', views.subir_epidemiologia, name='subir_epidemiologia'),
    path('procesar_archivos/<int:archivo_id>', views.procesar_archivos, name='procesar_archivos'),
    #Vehiculos
    path('buscar/vehiculo/', views.buscar_vehiculo, name='buscar_vehiculo'),
    path('lista/vehiculos', views.listar_vehiculos, name='listar_vehiculos'),
    path('vehiculos/tipo/<int:tipo_id>', views.listar_vehiculos, name='vehiculos_tipo'),
    path('ver/vehiculo/<int:vehiculo_id>', views.ver_vehiculo, name='ver_vehiculo'),
    path('cargar/vehiculo/<str:identificacion>', views.cargar_vehiculo, name='cargar_vehiculo'),
    path('mod/vehiculo/<int:vehiculo_id>', views.cargar_vehiculo, name='mod_vehiculo'),
    path('cargar/traslado/<int:vehiculo_id>', views.cargar_traslado, name='cargar_traslado'),
    #Individuos
    path('buscar/individuo/', views.buscar_individuo, name='buscar_individuo'),
    path('ver/individuo/<int:individuo_id>', views.ver_individuo, name='ver_individuo'),
    path('buscador/individuos', views.buscador_individuos, name='buscador_individuos'),
    path('arbol/relaciones/<int:individuo_id>', views.arbol_relaciones, name='arbol_relaciones'),
    #Tracking
    path('tracking/general', views.control_tracking, name='control_tracking'),
    path('tracking/<int:individuo_id>', views.ver_tracking, name='ver_tracking'),
    path('descartar/<int:geoposicion_id>', views.descartar_alerta, name='descartar_alerta'),
    #Listados
    path('lista/seguimiento', views.lista_seguimiento, name='lista_seguimiento'),
    path('lista/autodiagnosticos', views.lista_autodiagnosticos, name='lista_autodiagnosticos'),
    #Por parametro
    path('lista/nac/<int:nacionalidad_id>', views.lista_individuos, name='lista_nacionalidad'),
    path('lista/estado/<int:estado>', views.lista_individuos, name='lista_estado'),
    path('lista/conducta/<str:conducta>', views.lista_individuos, name='lista_conducta'),
    #Individuo
    path('cargar/individuo/<str:num_doc>', views.cargar_individuo, name='cargar_individuo'),
    path('cargar/pasajero/<int:traslado_id>', views.buscar_individuo, name='buscar_pasajero'),
    path('cargar/pasajero/<int:traslado_id>/nuevo/<int:individuo_id>/', views.cargar_individuo, name='cargar_pasajero'),
    path('cargar/pasajero/<int:traslado_id>/nuevo/<str:num_doc>/', views.cargar_individuo, name='cargar_pasajero_nuevo'),
    path('mod/individuo/<int:individuo_id>', views.cargar_individuo, name='mod_individuo'),
    #Domicilio
    path('cargar/domicilio/<int:individuo_id>', views.cargar_domicilio, name='cargar_domicilio'),
    path('mod/domicilio/<int:domicilio_id>', views.cargar_domicilio, name='mod_domicilio'),
    path('del/domicilio/<int:domicilio_id>', views.del_domicilio, name='del_domicilio'),
    #Fotografia
    path('cargar/fotografia/<int:individuo_id>', views.cargar_fotografia, name='cargar_fotografia'),
    #Turismo
    path('buscar/inquilino/<int:ubicacion_id>', views.buscar_inquilino, name='buscar_inquilino'),
    path('nuevo/inquilino/', views.cargar_inquilino, name='cargar_inquilino'),
    #Traslado
    path('traslado/elegir/ubicacion/<int:individuo_id>', views.elegir_ubicacion, name='elegir_ubicacion'),
    path('traslado/elegir/vehiculo/<int:individuo_id>/<int:ubicacion_id>', views.elegir_vehiculo, name='elegir_vehiculo'),
    path('trasladar/<int:individuo_id>/<int:ubicacion_id>/<int:vehiculo_id>', views.trasladar, name='trasladar'),
    #Signos vitales
    path('cargar/signosvitales/<int:individuo_id>', views.cargar_signosvitales, name='cargar_signosvitales'),
    path('mod/signosvitales/<int:individuo_id>/<int:signosvitales_id>', views.cargar_signosvitales, name='mod_signosvitales'),
    path('del/signosvitales/<int:signosvitales_id>', views.del_signosvitales, name='del_signosvitales'),
    #Situacion
    path('cargar/situacion/<int:individuo_id>', views.cargar_situacion, name='cargar_situacion'),
    path('mod/situacion/<int:situacion_id>', views.cargar_situacion, name='mod_situacion'),
    path('del/situacion/<int:situacion_id>', views.del_situacion, name='del_situacion'),
    #Seguimiento
    path('cargar/seguimiento/<int:individuo_id>', views.cargar_seguimiento, name='cargar_seguimiento'),
    path('mod/seguimiento/<int:individuo_id>/<int:seguimiento_id>', views.cargar_seguimiento, name='mod_seguimiento'),
    path('del/seguimiento/<int:seguimiento_id>', views.del_seguimiento, name='del_seguimiento'),
    #Relacion
    path('cargar/relacion/<int:individuo_id>', views.cargar_relacion, name='cargar_relacion'),
    path('mod/relacion/<int:individuo_id>/<int:relacion_id>', views.cargar_relacion, name='mod_relacion'),
    path('del/relacion/<int:relacion_id>', views.del_relacion, name='del_relacion'),
    #Atributos
    path('cargar/atributo/<int:individuo_id>', views.cargar_atributo, name='cargar_atributo'),
    path('mod/atributo/<int:individuo_id>/<int:atributo_id>', views.cargar_atributo, name='mod_atributo'),
    path('del/atributo/<int:atributo_id>', views.del_atributo, name='del_atributo'),
    #Sintoma
    path('cargar/sintoma/<int:individuo_id>', views.cargar_sintoma, name='cargar_sintoma'),
    path('mod/sintoma/<int:individuo_id>/<int:sintoma_id>', views.cargar_sintoma, name='mod_sintoma'),
    path('del/sintoma/<int:sintoma_id>', views.del_sintoma, name='del_sintoma'),
    #Documentos
    path('cargar/documento/<int:individuo_id>', views.cargar_documento, name='cargar_documento'),
    path('mod/documento/<int:individuo_id>/<int:documento_id>', views.cargar_documento, name='mod_documento'),
    path('del/documento/<int:documento_id>', views.del_documento, name='del_documento'),
    #Geopos
    path('cargar/geopos/<int:individuo_id>', views.cargar_geoposicion, name='cargar_geoposicion'),
    #Reportes
    path('tablero', views.tablero_control, name='tablero_control'),
    path('reporte/basico', views.reporte_basico, name='reporte_basico'),
    #Carga Masiva
    path('upload/epidemiologia', views.subir_epidemiologia, name='subir_epidemiologia'),
    path('upload/padron/individuos/', views.upload_padron_individuos, name='upload_padron_individuos'),
    path('upload/padron/domicilios/', views.upload_padron_domicilios, name='upload_padron_domicilios'),
    #Testing
    path('send/notificacion', views.enviar_notificacion, name='enviar_notificacion'),
    #Autocomplete
    #url(r'^sintomas-autocomplete/$', autocomplete.SintomaAutocomplete.as_view(), name='sintomas-autocomplete',),
    #url(r'^atributos-autocomplete/$', autocomplete.AtributoAutocomplete.as_view(), name='atributos-autocomplete',),
    url(r'^individuos-autocomplete/$', autocomplete.IndividuosAutocomplete.as_view(), name='individuos-autocomplete',),
]