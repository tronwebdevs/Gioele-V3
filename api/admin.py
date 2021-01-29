from django.contrib import admin
from django.contrib.auth.models import User

from .models import Visitor, GUser, Game


class APIAdminSite(admin.AdminSite):
    site_title = 'API Administration'
    site_header = 'API Administration'
    index_title = 'Administration'


class GameInline(admin.TabularInline):
    model = Game
    extra = 0


class GUserAdmin(admin.ModelAdmin):
    fields = ('auth', 'score')
    inlines = [GameInline]


admin_site = APIAdminSite(name='apiadmin')
admin_site.register(Visitor)
admin_site.register(GUser, GUserAdmin)
