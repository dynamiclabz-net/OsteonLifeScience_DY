from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import *


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'active', 'last_login')
    list_filter = ('role', 'is_staff', 'is_superuser', 'active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'contact_number')
    ordering = ('username',)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Osteon details', {'fields': ('role', 'contact_number', 'active')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Osteon details', {'fields': ('email', 'role', 'contact_number')}),
    )
