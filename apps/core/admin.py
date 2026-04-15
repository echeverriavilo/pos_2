from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Tenant, Role, Membership, Permission, StaffTenantAccess


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_platform_staff')
    list_filter = ('is_active', 'is_staff', 'is_platform_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    exclude = ('date_joined',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Platform', {'fields': ('is_platform_staff',)}),
        ('PIN', {'fields': ('pin_enabled',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    ordering = ('-created_at',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('name',)
    ordering = ('tenant', 'name')
    raw_id_fields = ('tenant',)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'role')
    list_filter = ('tenant', 'role')
    search_fields = ('user__email',)
    raw_id_fields = ('user', 'tenant', 'role')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'description')
    search_fields = ('codename', 'description')
    ordering = ('codename',)


@admin.register(StaffTenantAccess)
class StaffTenantAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('user__email',)
    raw_id_fields = ('user', 'tenant')