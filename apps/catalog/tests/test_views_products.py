import pytest
from django.test import override_settings
from django.urls import reverse

from apps.catalog.models import Category, Product
from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission
from apps.core.services.tenant import TenantService


@pytest.fixture
def tenant(db):
    return TenantService.create_tenant(slug='test-prod', name='Test Prod Tenant')


@pytest.fixture
def another_tenant(db):
    return TenantService.create_tenant(slug='other-prod', name='Other Prod Tenant')


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


@pytest.fixture
def categoria(tenant):
    return Category.objects.create(tenant=tenant, nombre='Bebidas')


def _host(tenant):
    return f'{tenant.slug}.localhost'


@pytest.mark.django_db
class TestProductList:
    def test_list_muestra_productos_del_tenant(self, admin_client, tenant, categoria):
        Product.objects.create(
            tenant=tenant, category=categoria, nombre='Coca-Cola', precio_bruto=1500,
        )
        Product.objects.create(
            tenant=tenant, category=categoria, nombre='Fanta', precio_bruto=1200,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('catalog:product-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Coca-Cola' in response.content
        assert b'Fanta' in response.content

    def test_list_no_muestra_productos_de_otro_tenant(self, admin_client, tenant, another_tenant, categoria):
        cat_other = Category.objects.create(tenant=another_tenant, nombre='Otro')
        Product.objects.create(
            tenant=tenant, category=categoria, nombre='Local', precio_bruto=500,
        )
        Product.objects.create(
            tenant=another_tenant, category=cat_other, nombre='Foraneo', precio_bruto=500,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('catalog:product-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Local' in response.content
        assert b'Foraneo' not in response.content

    def test_list_busqueda_filtra_por_nombre(self, admin_client, tenant, categoria):
        Product.objects.create(
            tenant=tenant, category=categoria, nombre='Hamburguesa', precio_bruto=5000,
        )
        Product.objects.create(
            tenant=tenant, category=categoria, nombre='Papas Fritas', precio_bruto=3000,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('catalog:product-list') + '?search=Hamburguesa',
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Hamburguesa' in response.content
        assert b'Papas Fritas' not in response.content

    def test_list_busqueda_filtra_por_descripcion(self, admin_client, tenant, categoria):
        Product.objects.create(
            tenant=tenant, category=categoria, nombre='Item A', precio_bruto=100,
            description='Descripción especial única',
        )
        Product.objects.create(
            tenant=tenant, category=categoria, nombre='Item B', precio_bruto=200,
            description='Otra descripción',
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('catalog:product-list') + '?search=especial',
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Item A' in response.content
        assert b'Item B' not in response.content


@pytest.mark.django_db
class TestProductCreate:
    def test_create_crea_producto_y_redirige(self, admin_client, tenant, categoria):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:product-create'),
                data={
                    'nombre': 'Pizza',
                    'category': categoria.pk,
                    'precio_bruto': '8000',
                    'es_inventariable': True,
                    'stock_actual': '50',
                    'description': 'Pizza familiar',
                },
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        assert response.url == reverse('catalog:product-list')
        assert Product.objects.for_tenant(tenant).filter(nombre='Pizza').exists()

    def test_create_rechaza_precio_negativo(self, admin_client, tenant, categoria):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:product-create'),
                data={
                    'nombre': 'Negativo',
                    'category': categoria.pk,
                    'precio_bruto': '-100',
                    'es_inventariable': True,
                    'stock_actual': '0',
                    'description': '',
                },
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert not Product.objects.for_tenant(tenant).filter(nombre='Negativo').exists()

    def test_create_sin_permiso_retorna_403(self, no_perm_client, tenant, categoria):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('catalog:product-create'),
                data={
                    'nombre': 'No Permitido',
                    'category': categoria.pk,
                    'precio_bruto': '100',
                },
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403


@pytest.mark.django_db
class TestProductEdit:
    def test_edit_actualiza_producto(self, admin_client, tenant, categoria):
        prod = Product.objects.create(
            tenant=tenant, category=categoria, nombre='Original', precio_bruto=1000,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:product-edit', kwargs={'pk': prod.pk}),
                data={
                    'nombre': 'Editado',
                    'category': categoria.pk,
                    'precio_bruto': '2000',
                    'es_inventariable': True,
                    'stock_actual': '10',
                    'description': 'Actualizado',
                },
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        prod.refresh_from_db()
        assert prod.nombre == 'Editado'
        assert prod.precio_bruto == 2000


@pytest.mark.django_db
class TestProductToggle:
    def test_toggle_desactiva_producto(self, admin_client, tenant, categoria):
        prod = Product.objects.create(
            tenant=tenant, category=categoria, nombre='Activo', precio_bruto=500,
            is_active=True,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:product-toggle', kwargs={'pk': prod.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        prod.refresh_from_db()
        assert prod.is_active is False

    def test_toggle_reactiva_producto(self, admin_client, tenant, categoria):
        prod = Product.objects.create(
            tenant=tenant, category=categoria, nombre='Inactivo', precio_bruto=500,
            is_active=False,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:product-toggle', kwargs={'pk': prod.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        prod.refresh_from_db()
        assert prod.is_active is True


@pytest.mark.django_db
class TestProductInhabilitar:
    def test_inhabilitar_producto(self, admin_client, tenant, categoria):
        prod = Product.objects.create(
            tenant=tenant, category=categoria, nombre='A borrar', precio_bruto=100,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('catalog:product-inhabilitar', kwargs={'pk': prod.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        prod.refresh_from_db()
        assert prod.inhabilitado is True
        assert prod.is_active is False

    def test_inhabilitar_oculta_de_lista(self, admin_client, tenant, categoria):
        prod = Product.objects.create(
            tenant=tenant, category=categoria, nombre='Oculto', precio_bruto=100,
            inhabilitado=True, is_active=False,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('catalog:product-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Oculto' not in response.content

    def test_inhabilitar_sin_permiso_retorna_403(self, no_perm_client, tenant, categoria):
        prod = Product.objects.create(
            tenant=tenant, category=categoria, nombre='Sin permiso', precio_bruto=100,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('catalog:product-inhabilitar', kwargs={'pk': prod.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403
