from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    ADMIN_MENU = [(name.capitalize() , name)]
    ADMIN_MODELS = {}