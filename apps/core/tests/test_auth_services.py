import pytest

from django.contrib.auth import get_user_model

from apps.core.models import CustomUser, Membership, Permission, Role, Tenant
from apps.core.services.auth import (
    AuthorizationError,
    validate_role_permission,
    validate_tenant_access,
)


@pytest.mark.django_db
class TestValidateTenantAccess:
    def test_platform_staff_can_access_any_tenant(self):
        user = CustomUser.objects.create_user(
            email='staff@platform.com',
            password='test123',
            is_platform_staff=True,
        )
        tenant = Tenant.objects.create(slug='tenant-a', name='Tenant A')

        result = validate_tenant_access(user, tenant)
        assert result is True

    def test_user_without_tenant_denied(self):
        user = CustomUser.objects.create_user(
            email='user@test.com',
            password='test123',
        )
        tenant = Tenant.objects.create(slug='tenant-b', name='Tenant B')

        with pytest.raises(AuthorizationError):
            validate_tenant_access(user, tenant)

    def test_user_with_different_tenant_denied(self):
        tenant_a = Tenant.objects.create(slug='tenant-a', name='Tenant A')
        tenant_b = Tenant.objects.create(slug='tenant-b', name='Tenant B')
        user = CustomUser.objects.create_user(
            email='user@tenant-a.com',
            password='test123',
        )
        Membership.objects.create(user=user, tenant=tenant_a)

        with pytest.raises(AuthorizationError):
            validate_tenant_access(user, tenant_b)

    def test_user_with_matching_tenant_allowed(self):
        tenant = Tenant.objects.create(slug='tenant-c', name='Tenant C')
        user = CustomUser.objects.create_user(
            email='user@tenant-c.com',
            password='test123',
        )
        Membership.objects.create(user=user, tenant=tenant)

        result = validate_tenant_access(user, tenant)
        assert result is True


@pytest.mark.django_db
class TestValidateRolePermission:
    def test_superuser_has_all_permissions(self):
        user = CustomUser.objects.create_user(
            email='admin@test.com',
            password='test123',
            is_superuser=True,
        )
        tenant = Tenant.objects.create(slug='tenant-d', name='Tenant D')
        Membership.objects.create(user=user, tenant=tenant)

        result = validate_role_permission(user, 'any_action')
        assert result is True

    def test_platform_staff_has_all_permissions(self):
        user = CustomUser.objects.create_user(
            email='staff2@platform.com',
            password='test123',
            is_platform_staff=True,
        )
        tenant = Tenant.objects.create(slug='tenant-e', name='Tenant E')
        Membership.objects.create(user=user, tenant=tenant)

        result = validate_role_permission(user, 'any_action')
        assert result is True

    def test_user_without_role_denied(self):
        user = CustomUser.objects.create_user(
            email='norole@test.com',
            password='test123',
        )
        tenant = Tenant.objects.create(slug='tenant-f', name='Tenant F')
        Membership.objects.create(user=user, tenant=tenant, role=None)

        with pytest.raises(AuthorizationError):
            validate_role_permission(user, 'some_action')

    def test_user_with_role_and_permission_allowed(self):
        tenant = Tenant.objects.create(slug='tenant-g', name='Tenant G')
        role = Role.objects.create(tenant=tenant, name='garzon')
        perm, _ = Permission.objects.get_or_create(codename='create_order')
        role.permissions.add(perm)

        user = CustomUser.objects.create_user(
            email='garzon@test.com',
            password='test123',
        )
        Membership.objects.create(user=user, tenant=tenant, role=role)

        result = validate_role_permission(user, 'create_order')
        assert result is True

    def test_user_without_permission_denied(self):
        tenant = Tenant.objects.create(slug='tenant-h', name='Tenant H')
        role = Role.objects.create(tenant=tenant, name='garzon')
        perm, _ = Permission.objects.get_or_create(codename='create_order')
        role.permissions.add(perm)

        user = CustomUser.objects.create_user(
            email='cajero@test.com',
            password='test123',
        )
        Membership.objects.create(user=user, tenant=tenant, role=role)

        with pytest.raises(AuthorizationError):
            validate_role_permission(user, 'register_payment')


@pytest.mark.django_db
class TestRolePermissions:
    def test_role_has_permission_method(self):
        tenant = Tenant.objects.create(slug='tenant-i', name='Tenant I')
        role = Role.objects.create(tenant=tenant, name='admin')
        perm, _ = Permission.objects.get_or_create(codename='manage_users')
        role.permissions.add(perm)

        assert role.has_permission('manage_users') is True
        assert role.has_permission('nonexistent') is False