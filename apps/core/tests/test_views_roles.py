import pytest
from django.test import override_settings
from django.urls import reverse

from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission
from apps.core.services.tenant import TenantService


@pytest.fixture
def tenant(db):
    return TenantService.create_tenant(slug='test-role', name='Test Role Tenant')


@pytest.fixture
def another_tenant(db):
    return TenantService.create_tenant(slug='other-role', name='Other Role Tenant')


@pytest.fixture
def admin_role(tenant):
    role = Role.objects.create(tenant=tenant, name='admin')
    for perm_codename in ['manage_users']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        RolePermission.objects.get_or_create(
            role=role, permission=perm, defaults={'active': True},
        )
    return role


@pytest.fixture
def admin_user(tenant, admin_role):
    user = CustomUser.objects.create_user(email='admin@test.com', password='testpass123')
    Membership.objects.create(user=user, tenant=tenant, role=admin_role)
    return user


@pytest.fixture
def no_perm_role(tenant):
    return Role.objects.create(tenant=tenant, name='sin_permisos')


@pytest.fixture
def no_perm_user(tenant, no_perm_role):
    user = CustomUser.objects.create_user(email='noperm@test.com', password='testpass123')
    Membership.objects.create(user=user, tenant=tenant, role=no_perm_role)
    return user


@pytest.fixture
def admin_client(admin_user):
    from django.test import Client
    c = Client()
    c.force_login(admin_user)
    return c


@pytest.fixture
def no_perm_client(no_perm_user):
    from django.test import Client
    c = Client()
    c.force_login(no_perm_user)
    return c


def _host(tenant):
    return f'{tenant.slug}.localhost'


@pytest.mark.django_db
class TestRoleList:
    def test_list_muestra_roles_del_tenant(self, admin_client, tenant):
        Role.objects.create(tenant=tenant, name='cocinero')
        Role.objects.create(tenant=tenant, name='bodeguero')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('core:role-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'cocinero' in response.content
        assert b'bodeguero' in response.content

    def test_list_no_muestra_roles_de_otro_tenant(self, admin_client, tenant, another_tenant):
        Role.objects.create(tenant=tenant, name='Local')
        Role.objects.create(tenant=another_tenant, name='Foraneo')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('core:role-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Local' in response.content
        assert b'Foraneo' not in response.content


@pytest.mark.django_db
class TestRoleCreate:
    def test_create_crea_rol_y_redirige(self, admin_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:role-create'),
                data={'name': 'supervisor', 'description': 'Rol de pruebas'},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        assert response.url == reverse('core:role-list')
        assert Role.objects.for_tenant(tenant).filter(name='supervisor').exists()

    def test_create_rechaza_nombre_vacio(self, admin_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:role-create'),
                data={'name': '', 'description': ''},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Este campo es obligatorio' in response.content or b'required' in response.content

    def test_create_sin_permiso_retorna_403(self, no_perm_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('core:role-create'),
                data={'name': 'No Autorizado'},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403


@pytest.mark.django_db
class TestRoleEdit:
    def test_edit_actualiza_rol(self, admin_client, tenant):
        role = Role.objects.create(tenant=tenant, name='antiguo', description='v1')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:role-edit', kwargs={'pk': role.pk}),
                data={'name': 'nuevo', 'description': 'v2'},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        role.refresh_from_db()
        assert role.name == 'nuevo'
        assert role.description == 'v2'


@pytest.mark.django_db
class TestRoleToggle:
    def test_toggle_desactiva_rol(self, admin_client, tenant):
        role = Role.objects.create(tenant=tenant, name='desactivar', is_active=True)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:role-toggle', kwargs={'pk': role.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        role.refresh_from_db()
        assert role.is_active is False

    def test_toggle_reactiva_rol(self, admin_client, tenant):
        role = Role.objects.create(tenant=tenant, name='reactivar', is_active=False)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:role-toggle', kwargs={'pk': role.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        role.refresh_from_db()
        assert role.is_active is True


@pytest.mark.django_db
class TestRoleInhabilitar:
    def test_inhabilitar_rol(self, admin_client, tenant):
        role = Role.objects.create(tenant=tenant, name='a borrar')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:role-inhabilitar', kwargs={'pk': role.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        role.refresh_from_db()
        assert role.inhabilitado is True
        assert role.is_active is False

    def test_inhabilitar_oculta_de_lista(self, admin_client, tenant):
        role = Role.objects.create(tenant=tenant, name='Oculto', inhabilitado=True, is_active=False)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('core:role-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Oculto' not in response.content

    def test_inhabilitar_sin_permiso_retorna_403(self, no_perm_client, tenant):
        role = Role.objects.create(tenant=tenant, name='Sin permiso')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('core:role-inhabilitar', kwargs={'pk': role.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403
