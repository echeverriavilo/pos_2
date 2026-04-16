import pytest
from django.urls import reverse

from apps.core.models import Role, Permission, Membership
from apps.core.services import tenant as tenant_service
from apps.dining.models import DiningTable
from apps.dining.services import DiningTableService
from apps.orders.models import Order


@pytest.fixture
def test_tenant():
    return tenant_service.TenantService.create_tenant(slug='test-dining-ui', name='Test UI', config_flujo_mesas=True)


@pytest.fixture
def waiter_user(django_user_model, test_tenant):
    user = django_user_model.objects.create_user(email='waiter@test.com', password='password123')
    role = Role.objects.create(tenant=test_tenant, name='waiter')
    for perm_codename in ['create_order', 'add_item', 'manage_tables']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        role.permissions.add(perm)
    Membership.objects.create(user=user, tenant=test_tenant, role=role)
    return user


@pytest.fixture
def test_table(waiter_user, test_tenant):
    return DiningTableService.create_table(user=waiter_user, tenant=test_tenant, numero='1')


@pytest.fixture
def test_product(test_tenant):
    from apps.catalog.models import Category, Product
    cat = Category.objects.create(tenant=test_tenant, nombre='Test')
    return Product.objects.create(
        tenant=test_tenant,
        category=cat,
        nombre='Test Product',
        precio_bruto=1000
    )


from django.test import override_settings

@pytest.mark.django_db
class TestDiningMapViews:
    def test_table_map_renders(self, client, waiter_user, test_tenant, test_table):
        client.force_login(waiter_user)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = client.get(reverse('dining:table-map'), HTTP_HOST=f"{test_tenant.slug}.localhost")
        assert response.status_code == 200
        assert 'tables' in response.context
        assert response.context['tables'].count() == 1
        # Verificamos fragmento de html
        assert b'Mesa 1' in response.content or b'1' in response.content
        assert b'bg-success' in response.content

    def test_table_open_modal_renders(self, client, waiter_user, test_tenant, test_table):
        client.force_login(waiter_user)
        with override_settings(ALLOWED_HOSTS=['*']):
            response = client.get(reverse('dining:table-open-modal', kwargs={'pk': test_table.pk}), HTTP_HOST=f"{test_tenant.slug}.localhost")
        assert response.status_code == 200
        # Verificamos presencia de modal y boton de submit
        assert b'openTableModal' in response.content
        assert b'Abrir y Tomar Pedido' in response.content

    def test_table_open_post_redirects_via_htmx(self, client, waiter_user, test_tenant, test_table):
        client.force_login(waiter_user)
        assert test_table.estado == DiningTable.States.DISPONIBLE
        
        with override_settings(ALLOWED_HOSTS=['*']):
            response = client.post(reverse('dining:table-open', kwargs={'pk': test_table.pk}), HTTP_HOST=f"{test_tenant.slug}.localhost")
        
        assert response.status_code == 204
        assert 'HX-Redirect' in response.headers
        assert response.headers['HX-Redirect'] == reverse('orders:mesa-pedido', kwargs={'table_id': test_table.pk})
        
        test_table.refresh_from_db()
        assert test_table.estado == DiningTable.States.OCUPADA
        assert client.session.get('order_id') is not None
        
        # Cleanup
        order = Order.objects.get(id=client.session.get('order_id'))
        assert order.table == test_table

    def test_table_redirect_post_redirects_via_htmx(self, client, waiter_user, test_tenant, test_table):
        client.force_login(waiter_user)
        # Setup mesa ocupada
        order = DiningTableService.open_table(user=waiter_user, table=test_table)
        
        # Clear session to ensure it sets it again
        session = client.session
        if 'order_id' in session:
            del session['order_id']
            session.save()
            
        with override_settings(ALLOWED_HOSTS=['*']):
            response = client.post(reverse('dining:table-redirect', kwargs={'pk': test_table.pk}), HTTP_HOST=f"{test_tenant.slug}.localhost")
        
        assert response.status_code == 204
        assert 'HX-Redirect' in response.headers
        assert response.headers['HX-Redirect'] == reverse('orders:mesa-pedido', kwargs={'table_id': test_table.pk})
        assert client.session.get('order_id') == order.id


@pytest.mark.django_db
class TestMesaConfirmarPedido:
    def test_confirmar_pedido_mesa_pagando_vuelve_ocupada(self, client, waiter_user, test_tenant, test_table, test_product):
        client.force_login(waiter_user)
        
        order = DiningTableService.open_table(user=waiter_user, table=test_table)
        assert test_table.estado == DiningTable.States.OCUPADA
        
        DiningTableService.set_table_paying(user=waiter_user, table=test_table)
        test_table.refresh_from_db()
        assert test_table.estado == DiningTable.States.PAGANDO
        
        import json
        with override_settings(ALLOWED_HOSTS=['*']):
            response = client.post(
                reverse('orders:mesa-confirmar', kwargs={'table_id': test_table.pk}),
                data=json.dumps({'items': [{'product_id': test_product.pk, 'cantidad': 1}]}),
                content_type='application/json',
                HTTP_HOST=f"{test_tenant.slug}.localhost"
            )
        
        test_table.refresh_from_db()
        assert test_table.estado == DiningTable.States.OCUPADA