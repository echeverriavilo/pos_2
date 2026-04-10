import pytest

from django.core.exceptions import ValidationError

from apps.core import tenant_context
from apps.core.models import CustomUser, Membership, Role
from apps.core.services import tenant as tenant_service


@pytest.mark.django_db
def test_tenant_creation_creates_base_roles():
    tenant = tenant_service.TenantService.create_tenant(slug='test1', name='Test Tenant')
    expected = set(tenant_service.BASE_ROLES)
    found = set(tenant.roles.values_list('name', flat=True))
    assert found == expected


@pytest.mark.django_db
def test_membership_links_user_to_tenant():
    tenant = tenant_service.TenantService.create_tenant(slug='membership', name='Membership Tenant')
    role = tenant.roles.first()
    user = CustomUser.objects.create_user(email='user@example.com', password='password123')
    membership = Membership.objects.create(user=user, tenant=tenant, role=role)
    assert user.tenant == tenant
    assert user.role == role
    assert membership.role == role


@pytest.mark.django_db
def test_pin_validation_flows():
    user = CustomUser.objects.create_user(email='pin@example.com', password='secret')
    with pytest.raises(ValidationError):
        user.set_pin('12')
    user.set_pin('1234')
    assert user.pin_enabled
    assert user.check_pin('1234')
    assert not user.check_pin('9999')


@pytest.mark.django_db
def test_tenant_aware_manager_respects_context():
    tenant_a = tenant_service.TenantService.create_tenant(slug='tenant-a', name='Tenant A')
    tenant_b = tenant_service.TenantService.create_tenant(slug='tenant-b', name='Tenant B')

    with tenant_context.tenant_scope(tenant_a):
        a_names = {role.name for role in Role.objects.all()}
    with tenant_context.tenant_scope(tenant_b):
        b_names = {role.name for role in Role.objects.all()}

    assert a_names == b_names == set(tenant_service.BASE_ROLES)
