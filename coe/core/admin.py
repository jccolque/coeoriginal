#Modulos de Django
from django.contrib import admin
#Modulos para no permitir escalacion de privilegios
from django.contrib.auth.admin import UserAdmin, User
from django.contrib.auth.models import Permission
#Imports de la app
from .models import Faq
#Models Ocultos
def register_hidden_models(*model_names):
    for m in model_names:
        ma = type(
            str(m)+'Admin',
            (admin.ModelAdmin,),
            {
                'get_model_perms': lambda self, request: {}
            })
        admin.site.register(m, ma)

#Modificacion del panel de administrador para no permitir escalacion de privilegios
class NewUserAdmin(UserAdmin):
    model = User
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(NewUserAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        user = kwargs['request'].user
        if not user.is_superuser:
            if db_field.name == 'groups':
                field.queryset = field.queryset.filter(id__in=[i.id for i in user.groups.all()])
            if db_field.name == 'user_permissions':
                field.queryset = field.queryset.filter(id__in=[i.id for i in user.user_permissions.all()])
            if db_field.name == 'is_superuser':
                field.widget.attrs['disabled'] = True
        return field

class PermissionAdmin(admin.ModelAdmin):
    model = Permission
    search_fields = ['name', 'codename', ]
    list_filter = ['content_type__app_label', ]

#Permitimos la administracion de los permisos
admin.site.register(Permission, PermissionAdmin)
#Registramos modificaciones para no permitir escalacion de privilegios
admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
#registramos nuestros admins
admin.site.register(Faq)