import pytest
from django.urls import reverse
from django.test import Client
from django.test import override_settings
from decimal import Decimal

from apps.catalog.models import Category, Product
from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission, Tenant
from apps.orders.models import Order, OrderItem
from apps.orders.services.order import create_order, add_or_update_item_in_order, remove_item_from_order, recalculate_total


def _create_garzon_user(tenant):
    user = CustomUser.objects.create_user(email=f'garzon@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='garzon')
    for perm_codename in ['create_order', 'add_item', 'remove_item', 'manage_tables']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        RolePermission.objects.get_or_create(role=role, permission=perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=['*'])
def test_terminal_ventas_view_loads_correctly():
    tenant = Tenant.objects.create(slug='test', name='Test')
    user = _create_garzon_user(tenant)
    client = Client()
    client.force_login(user)
    url = reverse('orders:terminal-ventas')
    response = client.get(url, HTTP_HOST='test.localhost')

    assert response.status_code == 200
    assert 'Terminal de Ventas' in response.content.decode()
    assert 'id="product-grid"' in response.content.decode()
    assert 'id="shopping-cart"' in response.content.decode()
    assert 'id="category-list"' in response.content.decode()


@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=['*'])
def test_product_list_partial_filters_by_category():
    tenant = Tenant.objects.create(slug='filtertest', name='Filter Test')
    user = _create_garzon_user(tenant)
    client = Client()
    client.force_login(user)

    category1 = Category.objects.create(tenant=tenant, nombre='Bebidas')
    category2 = Category.objects.create(tenant=tenant, nombre='Comida')
    product1 = Product.objects.create(tenant=tenant, category=category1, nombre='Coca-Cola', precio_bruto=Decimal('1000'), is_active=True)
    product2 = Product.objects.create(tenant=tenant, category=category2, nombre='Hamburguesa', precio_bruto=Decimal('5000'), is_active=True)

    url = reverse('orders:product-list-partial')
    response = client.get(f'{url}?category={category1.id}', HTTP_HOST='filtertest.localhost')

    assert response.status_code == 200
    assert product1.nombre in response.content.decode()
    assert product2.nombre not in response.content.decode()


@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=['*'])
def test_product_list_partial_searches_products():
    tenant = Tenant.objects.create(slug='searchtest', name='Search Test')
    user = _create_garzon_user(tenant)
    client = Client()
    client.force_login(user)

    category = Category.objects.create(tenant=tenant, nombre='General')
    product1 = Product.objects.create(tenant=tenant, category=category, nombre='Papas Fritas', precio_bruto=Decimal('2000'), is_active=True)
    product2 = Product.objects.create(tenant=tenant, category=category, nombre='Aros de Cebolla', precio_bruto=Decimal('2500'), is_active=True)

    url = reverse('orders:product-list-partial')
    response = client.get(f'{url}?search=Papas', HTTP_HOST='searchtest.localhost')

    assert response.status_code == 200
    assert product1.nombre in response.content.decode()
    assert product2.nombre not in response.content.decode()


@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=['*'])
def test_add_to_cart_adds_item_to_session_order():
    tenant = Tenant.objects.create(slug='cartaddtest', name='Cart Add Test')
    user = _create_garzon_user(tenant)
    client = Client()
    client.force_login(user)

    category = Category.objects.create(tenant=tenant, nombre='Bebidas')
    product = Product.objects.create(tenant=tenant, category=category, nombre='Jugo Natural', precio_bruto=Decimal('1800'), is_active=True)

    url = reverse('orders:add-to-cart', args=[product.id])
    response = client.post(url, HTTP_HOST='cartaddtest.localhost')

    assert response.status_code == 200
    assert 'Jugo Natural' in response.content.decode()
    assert Order.objects.count() == 1
    order = Order.objects.first()
    assert order.items.count() == 1
    assert order.total_bruto == Decimal('1800.00')
    assert client.session['order_id'] == order.id


@pytest.mark.django_db
@override_settings(ALLOWED_HOSTS=['*'])
def test_remove_from_cart_removes_item():
    tenant = Tenant.objects.create(slug='cartremovetest', name='Cart Remove Test')
    user = _create_garzon_user(tenant)
    client = Client()
    client.force_login(user)

    category = Category.objects.create(tenant=tenant, nombre='Bebidas')
    product1 = Product.objects.create(tenant=tenant, category=category, nombre='Jugo Natural', precio_bruto=Decimal('1800'), is_active=True)
    product2 = Product.objects.create(tenant=tenant, category=category, nombre='Agua Mineral', precio_bruto=Decimal('1200'), is_active=True)

    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    client.session['order_id'] = order.id
    item1 = add_or_update_item_in_order(user=user, order=order, product=product1, cantidad=1)
    item2 = add_or_update_item_in_order(user=user, order=order, product=product2, cantidad=1)

    assert order.items.count() == 2
    assert order.total_bruto == Decimal('3000.00')

    url = reverse('orders:remove-from-cart', args=[item1.id])
    response = client.post(url, HTTP_HOST='cartremovetest.localhost')

    assert response.status_code == 200
    assert 'Jugo Natural' not in response.content.decode()
    order.refresh_from_db()
    assert order.items.filter(estado=OrderItem.States.ANULADO).count() == 1
    assert order.total_bruto == Decimal('1200.00')
