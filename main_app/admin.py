from django.contrib import admin

from .models import Organization, CustomUser, Event


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'qrcode')


admin.site.register(Organization)
admin.site.register(CustomUser)
admin.site.register(Event)
