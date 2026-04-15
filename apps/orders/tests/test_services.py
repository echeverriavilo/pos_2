from decimal import Decimal

import pytest

from apps.catalog.models import Category, Product
from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission, Tenant
from apps.dining.models import DiningTable
from apps.orders.models import Order, OrderItem
from apps.orders.services import (
    OrderError,
    OrderItemError,
    OrderStateTransitionError,
    add_or_update_item_in_order,
    create_order,
    create_order_for_table,
    recalculate_total,
    remove_item_from_order,
    transition_order_state,
)


def _create_garzon_user(tenant):
    user = CustomUser.objects.create_user(email=f'garzon@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='garzon')
    for perm_codename in ['create_order', 'add_item', 'remove_item', 'manage_tables']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        RolePermission.objects.get_or_create(role=role, permission=perm)
    membership = Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


@pytest.mark.django_db
def test_create_order_for_table_requires_mesa():
    tenant = Tenant.objects.create(slug='mesa-test', name='Mesa Test')
    table = DiningTable.objects.create(tenant=tenant, numero='1')
    user = _create_garzon_user(tenant)
    order = create_order_for_table(user=user, table=table)
    assert order.tipo_flujo == Order.Flow.MESA
    assert order.estado == Order.States.ABIERTO
    assert order.table == table


@pytest.mark.django_db
def test_create_order_requires_table_when_flow_mesa():
    tenant = Tenant.objects.create(slug='mesa-validate', name='Mesa Validate')
    user = _create_garzon_user(tenant)
    with pytest.raises(OrderError):
        create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA)


@pytest.mark.django_db
def test_add_item_sets_states_and_total():
    tenant = Tenant.objects.create(slug='flujos', name='Flujos')
    user = _create_garzon_user(tenant)
    category = Category.objects.create(tenant=tenant, nombre='Bebidas')
    product = Product.objects.create(
        tenant=tenant,
        category=category,
        nombre='Café',
        precio_bruto=Decimal('1500.00'),
        es_inventariable=False,
        stock_actual=Decimal('10.00'),
    )
    mesa_order = create_order(
        user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA,
        table=DiningTable.objects.create(tenant=tenant, numero='10')
    )
    rapido_order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    mesa_item = add_or_update_item_in_order(user=user, order=mesa_order, product=product, cantidad=2)
    rapido_item = add_or_update_item_in_order(user=user, order=rapido_order, product=product, cantidad=1)
    assert mesa_item.estado == OrderItem.States.PREPARACION
    assert rapido_item.estado == OrderItem.States.PENDIENTE
    assert mesa_order.total_bruto == Decimal('3000.00')
    assert rapido_order.total_bruto == Decimal('1500.00')


@pytest.mark.django_db
def test_add_item_rejects_different_tenant():
    tenant_a = Tenant.objects.create(slug='tenant-a', name='Tenant A')
    tenant_b = Tenant.objects.create(slug='tenant-b', name='Tenant B')
    user_a = _create_garzon_user(tenant_a)
    category_b = Category.objects.create(tenant=tenant_b, nombre='Empanadas')
    product = Product.objects.create(
        tenant=tenant_b,
        category=category_b,
        nombre='Empanada',
        precio_bruto=Decimal('1200.00'),
        es_inventariable=False,
        stock_actual=Decimal('4.00'),
    )
    order = create_order(
        user=user_a, tenant=tenant_a, tipo_flujo=Order.Flow.MESA,
        table=DiningTable.objects.create(tenant=tenant_a, numero='99')
    )
    with pytest.raises(OrderItemError):
        add_or_update_item_in_order(user=user_a, order=order, product=product, cantidad=1)


@pytest.mark.django_db
def test_remove_item_recalculates_total():
    tenant = Tenant.objects.create(slug='removal', name='Removals')
    user = _create_garzon_user(tenant)
    category = Category.objects.create(tenant=tenant, nombre='Platos')
    product = Product.objects.create(
        tenant=tenant,
        category=category,
        nombre='Empanada',
        precio_bruto=Decimal('1200.00'),
        es_inventariable=False,
        stock_actual=Decimal('5.00'),
    )
    order = create_order(
        user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA,
        table=DiningTable.objects.create(tenant=tenant, numero='3')
    )
    item = add_or_update_item_in_order(user=user, order=order, product=product, cantidad=3)
    assert order.total_bruto == Decimal('3600.00')
    removed = remove_item_from_order(user=user, item=item)
    assert removed.estado == OrderItem.States.ANULADO
    assert order.total_bruto == Decimal('0')
    assert recalculate_total(order) == Decimal('0')


@pytest.mark.django_db
def test_transition_flow_mesa_requires_payment_for_completion():
    tenant = Tenant.objects.create(slug='mesa-flow', name='Mesa Flow')
    user = _create_garzon_user(tenant)
    category = Category.objects.create(tenant=tenant, nombre='Sopas')
    product = Product.objects.create(
        tenant=tenant,
        category=category,
        nombre='Crema',
        precio_bruto=Decimal('800.00'),
        es_inventariable=False,
        stock_actual=Decimal('2.00'),
    )
    order = create_order(
        user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA,
        table=DiningTable.objects.create(tenant=tenant, numero='5')
    )
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=2)
    transition_order_state(order=order, target_state=Order.States.PAGADO_PARCIAL)
    total_paid = Decimal('1600.00')
    transition_order_state(order=order, target_state=Order.States.COMPLETADO, total_pagado=total_paid)
    assert order.estado == Order.States.COMPLETADO


@pytest.mark.django_db
def test_transition_flow_rapido_requires_total_payment():
    tenant = Tenant.objects.create(slug='rapido-flow', name='Rápido Flow')
    user = _create_garzon_user(tenant)
    category = Category.objects.create(tenant=tenant, nombre='Tostadas')
    product = Product.objects.create(
        tenant=tenant,
        category=category,
        nombre='Tostada',
        precio_bruto=Decimal('700.00'),
        es_inventariable=False,
        stock_actual=Decimal('5.00'),
    )
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
    transition_order_state(order=order, target_state=Order.States.PAGADO_PARCIAL)
    with pytest.raises(OrderStateTransitionError):
        transition_order_state(order=order, target_state=Order.States.CONFIRMADO, total_pagado=Decimal('0'))
    transition_order_state(order=order, target_state=Order.States.CONFIRMADO, total_pagado=Decimal('700.00'))
    assert order.estado == Order.States.CONFIRMADO
