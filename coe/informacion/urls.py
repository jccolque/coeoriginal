#imports django
from django.conf.urls import url
from django.urls import path
#Import de modulos personales
from . import views
from . import autocomplete

#Definimos paths de la app
app_name = 'informacion'
urlpatterns = [
    #Administrador
    path('', views.menu, name='menu'),
    #Archivos
    path('lista/archivos/pendientes', views.archivos_pendientes, name='archivos_pendientes'),
    path('lista/archivos/procesados/<int:procesado>', views.archivos_pendientes, name='archivos_procesados'),
    path('ver_archivo/<int:archivo_id>', views.ver_archivo, name='ver_archivo'),
    path('subir/archivos', views.upload_archivos, name='subir_archivos'),
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
    #Por parametro
    path('lista/nac/<int:nacionalidad_id>', views.lista_individuos, name='lista_nacionalidad'),
    path('lista/estado/<int:estado>', views.lista_individuos, name='lista_estado'),
    path('lista/conducta/<str:conducta>', views.lista_individuos, name='lista_conducta'),
    #Individuo
    path('cargar/individuo/<str:num_doc>', views.cargar_individuo, name='cargar_individuo'),
    path('cargar/min/individuo', views.cargar_min_individuo, name='cargar_min_individuo'),
    path('cargar/pasajero/<int:traslado_id>', views.buscar_individuo, name='buscar_pasajero'),
    path('cargar/pasajero/<int:traslado_id>/nuevo/<int:individuo_id>/', views.cargar_individuo, name='cargar_pasajero'),
    path('cargar/pasajero/<int:traslado_id>/nuevo/<str:num_doc>/', views.cargar_individuo, name='cargar_pasajero_nuevo'),
    path('mod/individuo/<int:individuo_id>/<str:num_doc>/', views.mod_individuo, name='mod_individuo'),
    #cambios:
    path('mod/num_doc/<int:individuo_id>', views.mod_num_doc, name='mod_num_doc'),
    path('mod/telefono/<int:individuo_id>', views.mod_telefono, name='mod_telefono'),
    path('mod/email/<int:individuo_id>', views.mod_email, name='mod_email'),
    #Domicilio
    path('cargar/domicilio/<int:individuo_id>', views.cargar_domicilio, name='cargar_domicilio'),
    path('mod/domicilio/<int:domicilio_id>', views.cargar_domicilio, name='mod_domicilio'),
    path('volver/domicilio/<int:domicilio_id>', views.volver_domicilio, name='volver_domicilio'),
    path('del/domicilio/<int:domicilio_id>', views.del_domicilio, name='del_domicilio'),
    #Fotografia
    path('cargar/fotografia/<int:individuo_id>', views.cargar_fotografia, name='cargar_fotografia'),
    #Turismo
    path('buscar/inquilino/<int:ubicacion_id>', views.buscar_inquilino, name='buscar_inquilino'),
    path('mover_inquilino/<int:ubicacion_id>/<int:individuo_id>', views.confirmar_inquilino, name='confirmar_inquilino'),
    path('nuevo/inquilino/<int:ubicacion_id>/<str:num_doc>', views.cargar_inquilino, name='cargar_inquilino'),
    path('ingresos_hoteles', views.lista_ingresos_hoteles, name='lista_ingresos_hoteles'),
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
    #Patologia
    path('cargar/patologia/<int:individuo_id>', views.cargar_patologia, name='cargar_patologia'),
    path('mod/patologia/<int:individuo_id>/<int:patologia_id>', views.cargar_patologia, name='mod_patologia'),
    path('del/patologia/<int:patologia_id>', views.del_patologia, name='del_patologia'),
    #Relacion
    path('cargar/relacion/<int:individuo_id>', views.cargar_relacion, name='cargar_relacion'),
    path('mod/relacion/<int:individuo_id>/<int:relacion_id>', views.cargar_relacion, name='mod_relacion'),
    path('del/relacion/<int:relacion_id>', views.del_relacion, name='del_relacion'),
    #Atributos
    path('cargar/atributo/<int:individuo_id>', views.cargar_atributo, name='cargar_atributo'),
    path('cargar/atributo/<int:individuo_id>/tipo/<str:tipo>', views.cargar_atributo, name='cargar_atributo'),
    path('mod/atributo/<int:individuo_id>/<int:atributo_id>', views.cargar_atributo, name='mod_atributo'),
    path('del/atributo/<int:atributo_id>', views.del_atributo, name='del_atributo'),
    #Sintoma
    path('cargar/sintoma/<int:individuo_id>', views.cargar_sintoma, name='cargar_sintoma'),
    path('mod/sintoma/<int:individuo_id>/<int:sintoma_id>', views.cargar_sintoma, name='mod_sintoma'),
    path('del/sintoma/<int:sintoma_id>', views.del_sintoma, name='del_sintoma'),
    #Documentos
    path('cargar/documento/<int:individuo_id>', views.cargar_documento, name='cargar_documento'),
    path('cargar/documento/<int:individuo_id>/tipo/<str:tipo>', views.cargar_documento, name='cargar_documento'),
    path('mod/documento/<int:individuo_id>/<int:documento_id>', views.cargar_documento, name='mod_documento'),
    path('del/documento/<int:documento_id>', views.del_documento, name='del_documento'),
    #Laboral
    path('cargar/laboral/<int:individuo_id>', views.cargar_laboral, name='cargar_laboral'),
    path('mod/laboral/<int:individuo_id>/<int:laboral_id>', views.cargar_laboral, name='mod_laboral'),
    path('del/laboral/<int:laboral_id>', views.del_laboral, name='del_laboral'),
    #Geopos
    path('cargar/geopos/<int:individuo_id>', views.cargar_geoposicion, name='cargar_geoposicion'),
    #Reportes
    path('tablero', views.tablero_control, name='tablero_control'),
    path('reporte/basico', views.reporte_por_filtros, name='reporte_por_filtros'),
    #Autocomplete
    #url(r'^sintomas-autocomplete/$', autocomplete.SintomaAutocomplete.as_view(), name='sintomas-autocomplete',),
    #url(r'^atributos-autocomplete/$', autocomplete.AtributoAutocomplete.as_view(), name='atributos-autocomplete',),
    url(r'^individuos-autocomplete/$', autocomplete.IndividuosAutocomplete.as_view(), name='individuos-autocomplete',),
    url(r'^vehiculos-operativo-autocomplete/$', autocomplete.VehiculosOperativoAutocomplete.as_view(), name='vehiculos-operativo-autocomplete',),
    url(r'^subtipolaboral-autocomplete/$', autocomplete.SubtipoLaboralAutocomplete.as_view(), name='subtipolaboral-autocomplete',),
]