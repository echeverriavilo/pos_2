import pytest
from django.test import override_settings
from django.urls import reverse

from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission
from apps.core.services.tenant import TenantService
from apps.orders.models import PaymentMethod


@pytest.fixture
def tenant(db):
    return TenantService.create_tenant(slug='test-pm', name='Test PM Tenant')


@pytest.fixture
def another_tenant(db):
    return TenantService.create_tenant(slug='other-pm', name='Other PM Tenant')


@pytest.fixture
def admin_role(tenant):
    role = Role.objects.create(tenant=tenant, name='admin')
    for perm_codename in ['manage_cash_registers']:
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
class TestPaymentMethodList:
    def test_list_muestra_metodos_de_pago_del_tenant(self, admin_client, tenant):
        PaymentMethod.objects.create(tenant=tenant, nombre='Cheque', orden=10)
        PaymentMethod.objects.create(tenant=tenant, nombre='QR', orden=20)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('orders:payment-method-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Cheque' in response.content
        assert b'QR' in response.content

    def test_list_no_muestra_metodos_de_otro_tenant(self, admin_client, tenant, another_tenant):
        PaymentMethod.objects.create(tenant=tenant, nombre='Local', orden=1)
        PaymentMethod.objects.create(tenant=another_tenant, nombre='Foraneo', orden=1)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('orders:payment-method-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Local' in response.content
        assert b'Foraneo' not in response.content


@pytest.mark.django_db
class TestPaymentMethodCreate:
    def test_create_crea_metodo_y_redirige(self, admin_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('orders:payment-method-create'),
                data={'nombre': 'Cripto', 'orden': 5},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        assert response.url == reverse('orders:payment-method-list')
        assert PaymentMethod.objects.for_tenant(tenant).filter(nombre='Cripto').exists()

    def test_create_rechaza_nombre_vacio(self, admin_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('orders:payment-method-create'),
                data={'nombre': '', 'orden': 1},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Este campo es obligatorio' in response.content or b'required' in response.content

    def test_create_sin_permiso_retorna_403(self, no_perm_client, tenant):
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('orders:payment-method-create'),
                data={'nombre': 'No Permitido', 'orden': 1},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403


@pytest.mark.django_db
class TestPaymentMethodEdit:
    def test_edit_actualiza_metodo(self, admin_client, tenant):
        pm = PaymentMethod.objects.create(tenant=tenant, nombre='Original', orden=1)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('orders:payment-method-edit', kwargs={'pk': pm.pk}),
                data={'nombre': 'Editado', 'orden': 99},
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        pm.refresh_from_db()
        assert pm.nombre == 'Editado'
        assert pm.orden == 99


@pytest.mark.django_db
class TestPaymentMethodToggle:
    def test_toggle_desactiva_metodo(self, admin_client, tenant):
        pm = PaymentMethod.objects.create(tenant=tenant, nombre='Activo', orden=1, activo=True)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('orders:payment-method-toggle', kwargs={'pk': pm.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        pm.refresh_from_db()
        assert pm.activo is False

    def test_toggle_reactiva_metodo(self, admin_client, tenant):
        pm = PaymentMethod.objects.create(tenant=tenant, nombre='Inactivo', orden=1, activo=False)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('orders:payment-method-toggle', kwargs={'pk': pm.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        pm.refresh_from_db()
        assert pm.activo is True


@pytest.mark.django_db
class TestPaymentMethodInhabilitar:
    def test_inhabilitar_metodo(self, admin_client, tenant):
        pm = PaymentMethod.objects.create(tenant=tenant, nombre='A borrar', orden=1)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.post(
                reverse('orders:payment-method-inhabilitar', kwargs={'pk': pm.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 302
        pm.refresh_from_db()
        assert pm.inhabilitado is True
        assert pm.activo is False

    def test_inhabilitar_oculta_de_lista(self, admin_client, tenant):
        pm = PaymentMethod.objects.create(
            tenant=tenant, nombre='Oculto', orden=1,
            inhabilitado=True, activo=False,
        )
        with override_settings(ALLOWED_HOSTS=['*']):
            response = admin_client.get(
                reverse('orders:payment-method-list'), HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 200
        assert b'Oculto' not in response.content

    def test_inhabilitar_sin_permiso_retorna_403(self, no_perm_client, tenant):
        pm = PaymentMethod.objects.create(tenant=tenant, nombre='Sin permiso', orden=1)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = no_perm_client.post(
                reverse('orders:payment-method-inhabilitar', kwargs={'pk': pm.pk}),
                HTTP_HOST=_host(tenant),
            )
        assert response.status_code == 403
