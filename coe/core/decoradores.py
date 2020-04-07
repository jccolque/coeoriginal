#Imports de django
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

#Nuestros decoradores
def superuser_required(function):
    def vista(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return vista

def any_permission_required(*args):
    def vista(user):
        for perm in args:
            if user.has_perm(perm):
                return True
        return False
    return user_passes_test(vista)

def generic_permission_required(*args):
    def vista(user):
        for perm in user.get_all_permissions():
            if perm.split('.')[1] in args:
                return True
        return False
    return user_passes_test(vista)