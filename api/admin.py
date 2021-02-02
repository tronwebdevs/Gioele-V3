from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import GUser, VisitLog, LoginLog, MatchLog, UserInventory, Gun, Skin


class APIAdminSite(admin.AdminSite):
    site_title = 'API Administration'
    site_header = 'API Administration'
    index_title = 'Administration'


class MatchInline(admin.TabularInline):
    model = MatchLog
    extra = 0


class UserInventoryInline(admin.StackedInline):
    model = UserInventory
    can_delete = False


class GUserInline(admin.StackedInline):
    model = GUser
    can_delete = False
    inlines = (UserInventoryInline,)


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': ('username', 'password', 'email',)
            }
        ),
        # ('Permissions', { 'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), }),
        (
            'Timestamps',
            {
                'fields': ('last_login', 'date_joined')
            }
        ),
    )
    list_display = ('id', 'username', 'email', 'is_staff')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('id', 'username', 'email')
    ordering = ('id',)
    filter_horizontal = ('groups', 'user_permissions',)
    inlines = (GUserInline,)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price',)
    search_fields = ('username',)

admin_site = APIAdminSite(name='apiadmin')
admin_site.register(VisitLog)
admin_site.register(LoginLog)
admin_site.register(Gun, ItemAdmin)
admin_site.register(Skin, ItemAdmin)
admin_site.register(User, UserAdmin)
