import pytest
from django.test import override_settings
from django.urls import reverse

from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission
from apps.core.services.tenant import TenantService


@pytest.fixture
def tenant(db):
    return TenantService.create_tenant(slug='test-user', name='Test User Tenant')


@pytest.fixture
def another_tenant(db):
    return TenantService.create_tenant(slug='other-user', name='Other User Tenant')


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
def base_role(tenant):
    role, _ = Role.objects.get_or_create(tenant=tenant, name='cajero')
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
class TestUserList:
    def test_list_muestra_usuarios_del_tenant(self, admin_client, tenant, base_role):
        u1 = CustomUser.objects.create_user(email='u1@test.com', password='testpass123')
        Membership.objects.create(user=u1, tenant=tenant, role=base_role)
        u2 = CustomUser.objects.create_user(email='u2@test.com', password='testpass123')
        Membership.objects.create(user=u2, tenant=tenant, role=base_role)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('core:user-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'u1@test.com' in response.content
        assert b'u2@test.com' in response.content

    def test_list_no_muestra_usuarios_de_otro_tenant(self, admin_client, tenant, another_tenant):
        role_other = Role.objects.create(tenant=another_tenant, name='ext')
        u_local = CustomUser.objects.create_user(email='local@test.com', password='testpass123')
        Membership.objects.create(user=u_local, tenant=tenant, role=Role.objects.for_tenant(tenant).first())
        u_other = CustomUser.objects.create_user(email='other@test.com', password='testpass123')
        Membership.objects.create(user=u_other, tenant=another_tenant, role=role_other)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('core:user-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'local@test.com' in response.content
        assert b'other@test.com' not in response.content


@pytest.mark.django_db
class TestUserCreate:
    def test_create_crea_usuario_y_redirige(self, admin_client, tenant, base_role):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:user-create'),
                data={
                    'email': 'nuevo@test.com',
                    'password': 'pass123456',
                    'first_name': 'Nuevo',
                    'last_name': 'Usuario',
                    'role': base_role.pk,
                },
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        assert response.url == reverse('core:user-list')
        user = CustomUser.objects.get(email='nuevo@test.com')
        assert user.membership.tenant == tenant
        assert user.membership.role == base_role

    def test_create_rechaza_sin_password(self, admin_client, tenant, base_role):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:user-create'),
                data={
                    'email': 'sinpass@test.com',
                    'password': '',
                    'role': base_role.pk,
                },
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert not CustomUser.objects.filter(email='sinpass@test.com').exists()

    def test_create_sin_permiso_retorna_403(self, no_perm_client, tenant, base_role):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('core:user-create'),
                data={
                    'email': 'nop@test.com',
                    'password': 'pass123456',
                    'role': base_role.pk,
                },
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403


@pytest.mark.django_db
class TestUserEdit:
    def test_edit_actualiza_usuario(self, admin_client, tenant, base_role):
        user = CustomUser.objects.create_user(email='edit@test.com', password='testpass123')
        Membership.objects.create(user=user, tenant=tenant, role=base_role)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:user-edit', kwargs={'pk': str(user.pk)}),
                data={
                    'email': 'editado@test.com',
                    'first_name': 'Editado',
                    'last_name': 'Apellido',
                    'role': base_role.pk,
                    'password': '',
                },
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        assert response.url == reverse('core:user-list')
        user = CustomUser.objects.get(pk=user.pk)
        assert user.email == 'editado@test.com', f"email={user.email}, expected=editado@test.com"
        assert user.first_name == 'Editado'
        assert user.last_name == 'Apellido'

    def test_edit_no_muestra_usuarios_de_otro_tenant(self, admin_client, tenant, another_tenant):
        role_other = Role.objects.create(tenant=another_tenant, name='ext')
        user_other = CustomUser.objects.create_user(email='foreign@test.com', password='testpass123')
        Membership.objects.create(user=user_other, tenant=another_tenant, role=role_other)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('core:user-edit', kwargs={'pk': str(user_other.pk)}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 404


@pytest.mark.django_db
class TestUserToggle:
    def test_pausar_usuario(self, admin_client, tenant, base_role):
        """Al pausar, el campo pausado pasa a True."""
        user = CustomUser.objects.create_user(email='activo@test.com', password='testpass123')
        Membership.objects.create(user=user, tenant=tenant, role=base_role)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:user-toggle', kwargs={'pk': str(user.pk)}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.pausado is True

    def test_reanudar_usuario(self, admin_client, tenant, base_role):
        """Al reanudar, el campo pausado vuelve a False."""
        user = CustomUser.objects.create_user(
            email='inactivo@test.com', password='testpass123', pausado=True,
        )
        Membership.objects.create(user=user, tenant=tenant, role=base_role)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:user-toggle', kwargs={'pk': str(user.pk)}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.pausado is False


@pytest.mark.django_db
class TestUserInhabilitar:
    def test_inhabilitar_usuario(self, admin_client, tenant, base_role):
        """Inhabilitar deja inhabilitado=True e is_active=False."""
        user = CustomUser.objects.create_user(email='bye@test.com', password='testpass123')
        Membership.objects.create(user=user, tenant=tenant, role=base_role)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('core:user-inhabilitar', kwargs={'pk': str(user.pk)}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.inhabilitado is True
        assert user.is_active is False

    def test_inhabilitar_oculta_de_lista(self, admin_client, tenant, base_role):
        """Un usuario inhabilitado no aparece en la lista."""
        user = CustomUser.objects.create_user(email='oculto@test.com', password='testpass123')
        Membership.objects.create(user=user, tenant=tenant, role=base_role)
        user.inhabilitado = True
        user.save()
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('core:user-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'oculto@test.com' not in response.content

    def test_inhabilitar_sin_permiso_retorna_403(self, no_perm_client, tenant, base_role):
        user = CustomUser.objects.create_user(email='nop@test.com', password='testpass123')
        Membership.objects.create(user=user, tenant=tenant, role=base_role)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('core:user-inhabilitar', kwargs={'pk': str(user.pk)}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403
