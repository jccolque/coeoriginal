#Imports Django
from django.contrib import admin
#Imports extras

#Imports de la app
from .models import Rubro, SubGrupo
from .models import Item, EventoItem

#Definimos los inlines:
class SubGrupoInline(admin.TabularInline):
    model = SubGrupo
    fk_name = 'rubro'
    def has_delete_permission(self, request, obj=None):
        return False

class EventoItemInline(admin.TabularInline):
    model = EventoItem
    fk_name = 'item'
    readonly_fields = ('item',)
    extra = 0
    def has_delete_permission(self, request, obj=None):
        return False

#Definimos nuestros modelos administrables:
class RubroAdmin(admin.ModelAdmin):
    model = Rubro
    search_fields = ['nombre']
    inlines = [SubGrupoInline]
    def has_delete_permission(self, request, obj=None):
        return False

class ItemAdmin(admin.ModelAdmin):
    model = Item
    search_fields = ['nombre', 'actuante', 'responsable']
    inlines = [EventoItemInline]
    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(Rubro, RubroAdmin)
admin.site.register(Item, ItemAdmin)