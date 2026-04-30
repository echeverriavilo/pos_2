import pytest
from django.test import override_settings
from django.urls import reverse

from apps.catalog.models import Category
from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission, Tenant
from apps.core.services.tenant import TenantService


@pytest.fixture
def tenant(db):
    return TenantService.create_tenant(slug='test-cat', name='Test Cat Tenant')


@pytest.fixture
def another_tenant(db):
    return TenantService.create_tenant(slug='other-cat', name='Other Cat Tenant')


@pytest.fixture
def admin_role(tenant):
    role = Role.objects.create(tenant=tenant, name='admin')
    for perm_codename in ['manage_inventory']:
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
class TestCategoryList:
    def test_list_muestra_categorias_del_tenant(self, admin_client, tenant):
        Category.objects.create(tenant=tenant, nombre='Bebidas')
        Category.objects.create(tenant=tenant, nombre='Comidas')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('catalog:category-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Bebidas' in response.content
        assert b'Comidas' in response.content

    def test_list_no_muestra_categorias_de_otro_tenant(self, admin_client, tenant, another_tenant):
        Category.objects.create(tenant=tenant, nombre='Local')
        Category.objects.create(tenant=another_tenant, nombre='Foranea')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('catalog:category-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Local' in response.content
        assert b'Foranea' not in response.content


@pytest.mark.django_db
class TestCategoryCreate:
    def test_create_crea_categoria_y_redirige(self, admin_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:category-create'),
                data={'nombre': 'Postres'},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        assert response.url == reverse('catalog:category-list')
        assert Category.objects.for_tenant(tenant).filter(nombre='Postres').exists()

    def test_create_rechaza_nombre_vacio(self, admin_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:category-create'),
                data={'nombre': ''},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Este campo es obligatorio' in response.content or b'required' in response.content

    def test_create_sin_permiso_retorna_403(self, no_perm_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('catalog:category-create'),
                data={'nombre': 'Invitado'},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403


@pytest.mark.django_db
class TestCategoryEdit:
    def test_edit_actualiza_nombre(self, admin_client, tenant):
        cat = Category.objects.create(tenant=tenant, nombre='Original')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:category-edit', kwargs={'pk': cat.pk}),
                data={'nombre': 'Editado'},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        cat.refresh_from_db()
        assert cat.nombre == 'Editado'


@pytest.mark.django_db
class TestCategoryToggle:
    def test_toggle_desactiva_categoria(self, admin_client, tenant):
        cat = Category.objects.create(tenant=tenant, nombre='Activa', is_active=True)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:category-toggle', kwargs={'pk': cat.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        cat.refresh_from_db()
        assert cat.is_active is False

    def test_toggle_reactiva_categoria(self, admin_client, tenant):
        cat = Category.objects.create(tenant=tenant, nombre='Inactiva', is_active=False)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:category-toggle', kwargs={'pk': cat.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        cat.refresh_from_db()
        assert cat.is_active is True


@pytest.mark.django_db
class TestCategoryInhabilitar:
    def test_inhabilitar_categoria(self, admin_client, tenant):
        """Inhabilitar deja inhabilitado=True e is_active=False."""
        cat = Category.objects.create(tenant=tenant, nombre='A borrar')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:category-inhabilitar', kwargs={'pk': cat.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        cat.refresh_from_db()
        assert cat.inhabilitado is True
        assert cat.is_active is False

    def test_inhabilitar_oculta_de_lista(self, admin_client, tenant):
        """Una categoría inhabilitada no aparece en la lista."""
        cat = Category.objects.create(tenant=tenant, nombre='Oculta', inhabilitado=True, is_active=False)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('catalog:category-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Oculta' not in response.content

    def test_inhabilitar_sin_permiso_retorna_403(self, no_perm_client, tenant):
        cat = Category.objects.create(tenant=tenant, nombre='Sin permiso')
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('catalog:category-inhabilitar', kwargs={'pk': cat.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403
