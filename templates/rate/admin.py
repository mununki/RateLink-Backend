from django.contrib import admin
from .models import CNTRtype, Client, Rate


class CNTRtypeAdmin(admin.ModelAdmin):
    list_display = ('name', )


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'salesman', 'remarks', )


class RateAdmin(admin.ModelAdmin):
    list_display = ('inputperson', 'account', 'liner', 'pol', 'pod', 'type', 'buying20', 'buying40',
                    'buying4H', 'selling20', 'selling40', 'selling4H', 'offeredDate', 'effectiveDate', )


admin.site.register(Rate, RateAdmin)
admin.site.register(CNTRtype, CNTRtypeAdmin)
admin.site.register(Client, ClientAdmin)
