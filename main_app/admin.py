from django.contrib import admin
from .models import User, Organization, Event

admin.site.register(User)
admin.site.register(Organization)
admin.site.register(Event)
