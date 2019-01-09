from django.contrib import admin
from .models import Location
from .models import Liner


class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'label']
    ordering = ['name']
    search_fields = ['name', 'country', 'label']

class LinerAdmin(admin.ModelAdmin):
    list_display = ('name', 'label')
    ordering = ['name']
    search_fields = ['name', 'label']

admin.site.register(Location, LocationAdmin)
admin.site.register(Liner, LinerAdmin)