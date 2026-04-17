from decimal import Decimal

import pytest

from apps.catalog.models import Category, Product
from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission, Tenant
from apps.dining.models import DiningTable
from apps.orders.models import Order, OrderItem, Transaction
from apps.orders.selectors import TransactionSelector
from apps.orders.selectors.order_item import OrderItemSelector
from apps.orders.services import (
    PaymentCalculatorError,
    TransactionError,
    add_or_update_item_in_order,
    calculate_iva_breakdown,
    calculate_suggested_tip,
    create_order,
    register_transaction,
    remove_item_from_order,
    set_tip,
)


def _create_product(*, tenant, name, price, inventariable=False, stock='20.00'):
    category, _ = Category.objects.get_or_create(tenant=tenant, nombre='General')
    return Product.objects.create(
        tenant=tenant,
        category=category,
        nombre=name,
        precio_bruto=Decimal(price),
        es_inventariable=inventariable,
        stock_actual=Decimal(stock),
    )


def _create_cajero_user(tenant):
    user = CustomUser.objects.create_user(email=f'cajero@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='cajero')
    perm, _ = Permission.objects.get_or_create(codename='register_payment')
    RolePermission.objects.get_or_create(role=role, permission=perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


def _create_garzon_user(tenant):
    user = CustomUser.objects.create_user(email=f'garzon@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='garzon')
    for perm_codename in ['create_order', 'add_item', 'remove_item', 'manage_tables']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        RolePermission.objects.get_or_create(role=role, permission=perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


@pytest.mark.django_db
def test_calculate_iva_breakdown_returns_correct_values():
    """Verifica que el desglose de IVA calcula neto e IVA correctamente."""
    tenant = Tenant.objects.create(slug='iva-test', name='IVA Test', config_iva=Decimal('0.19'))
    user = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T1')
    product = _create_product(tenant=tenant, name='Plato', price='11900.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)

    breakdown = calculate_iva_breakdown(order, tenant)

    assert breakdown['total_bruto'] == Decimal('11900.00')
    assert breakdown['neto'] == Decimal('10000.00')
    assert breakdown['iva'] == Decimal('1900.00')


@pytest.mark.django_db
def test_calculate_iva_breakdown_with_different_rate():
    """Verifica que el desglose funciona con una tasa de IVA diferente."""
    tenant = Tenant.objects.create(slug='iva-low', name='IVA Low', config_iva=Decimal('0.10'))
    user = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T2')
    product = _create_product(tenant=tenant, name='Item', price='11000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)

    breakdown = calculate_iva_breakdown(order, tenant)

    assert breakdown['neto'] == Decimal('10000.00')
    assert breakdown['iva'] == Decimal('1000.00')


@pytest.mark.django_db
def test_calculate_suggested_tip_returns_10_percent():
    """Verifica que la propina sugerida es exactamente 10% del total bruto."""
    tenant = Tenant.objects.create(slug='tip-test', name='Tip Test')
    user = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T3')
    product = _create_product(tenant=tenant, name='Plato', price='50000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)

    tip = calculate_suggested_tip(order)

    assert tip == Decimal('5000.00')


@pytest.mark.django_db
def test_set_tip_updates_order_propina_monto():
    """Verifica que set_tip actualiza el monto de propina en la orden."""
    tenant = Tenant.objects.create(slug='set-tip', name='Set Tip')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T4')
    product = _create_product(tenant=tenant, name='Plato', price='10000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=1)

    updated_order = set_tip(user=user_cajero, order=order, amount=Decimal('1500.00'))

    order.refresh_from_db()
    assert order.propina_monto == Decimal('1500.00')
    assert updated_order.propina_monto == Decimal('1500.00')


@pytest.mark.django_db
def test_set_tip_rejects_on_completed_order():
    """Verifica que no se puede modificar propina en orden completada."""
    tenant = Tenant.objects.create(slug='tip-blocked', name='Tip Blocked')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T5')
    product = _create_product(tenant=tenant, name='Plato', price='5000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=1)

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.TOTAL)
    order.refresh_from_db()
    assert order.estado == Order.States.COMPLETADO

    with pytest.raises(PaymentCalculatorError):
        set_tip(user=user_cajero, order=order, amount=Decimal('500.00'))


@pytest.mark.django_db
def test_set_tip_rejects_negative_amount():
    """Verifica que set_tip rechaza montos negativos."""
    tenant = Tenant.objects.create(slug='tip-negative', name='Tip Negative')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T6')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)

    with pytest.raises(PaymentCalculatorError):
        set_tip(user=user_cajero, order=order, amount=Decimal('-100.00'))


@pytest.mark.django_db
def test_payment_with_tip_completes_when_total_cuenta_covered():
    """Verifica que una orden se completa pagando total_bruto + propina."""
    tenant = Tenant.objects.create(slug='tip-complete', name='Tip Complete')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T7')
    product = _create_product(tenant=tenant, name='Plato', price='10000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=1)

    set_tip(user=user_cajero, order=order, amount=Decimal('1000.00'))
    order.refresh_from_db()

    assert TransactionSelector.total_cuenta(order) == Decimal('11000.00')

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.TOTAL)

    order.refresh_from_db()
    assert order.estado == Order.States.COMPLETADO
    assert TransactionSelector.total_paid(order) == Decimal('11000.00')


@pytest.mark.django_db
def test_total_cuenta_includes_propina():
    """Verifica que total_cuenta incluye propina_monto."""
    tenant = Tenant.objects.create(slug='cuenta-check', name='Cuenta Check')
    user = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T8')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    order.total_bruto = Decimal('50000.00')
    order.propina_monto = Decimal('5000.00')
    order.save()

    assert TransactionSelector.total_cuenta(order) == Decimal('55000.00')


@pytest.mark.django_db
def test_total_pending_includes_propina():
    """Verifica que total_pending considera la propina en el cálculo."""
    tenant = Tenant.objects.create(slug='pending-tip', name='Pending Tip')
    user = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T9')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    order.total_bruto = Decimal('10000.00')
    order.propina_monto = Decimal('1000.00')
    order.save()

    assert TransactionSelector.total_pending(order) == Decimal('11000.00')


@pytest.mark.django_db
def test_total_payment_includes_tip_amount():
    """Verifica que el pago TOTAL incluye el monto de propina."""
    tenant = Tenant.objects.create(slug='total-tip', name='Total Tip')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T10')
    product = _create_product(tenant=tenant, name='Item', price='20000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=1)

    set_tip(user=user_cajero, order=order, amount=Decimal('2000.00'))
    order.refresh_from_db()

    transaction = register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.TOTAL)

    assert transaction.monto == Decimal('22000.00')


@pytest.mark.django_db
def test_set_tip_zero_removes_tip():
    """Verifica que se puede establecer propina en 0."""
    tenant = Tenant.objects.create(slug='tip-zero', name='Tip Zero')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T11')
    product = _create_product(tenant=tenant, name='Plato', price='10000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=1)

    set_tip(user=user_cajero, order=order, amount=Decimal('1000.00'))
    order.refresh_from_db()
    assert order.propina_monto == Decimal('1000.00')

    set_tip(user=user_cajero, order=order, amount=Decimal('0'))
    order.refresh_from_db()
    assert order.propina_monto == Decimal('0')


@pytest.mark.django_db
def test_multiple_abonos_complete_order_with_tip():
    """Verifica que múltiples abonos pueden completar una orden con propina."""
    tenant = Tenant.objects.create(slug='abonos-tip', name='Abonos Tip')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T12')
    product = _create_product(tenant=tenant, name='Pizza', price='10000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=1)

    set_tip(user=user_cajero, order=order, amount=Decimal('1000.00'))
    order.refresh_from_db()

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.ABONO, amount=Decimal('5000.00'))
    order.refresh_from_db()
    assert order.estado == Order.States.PAGADO_PARCIAL
    assert TransactionSelector.total_pending(order) == Decimal('6000.00')

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.ABONO, amount=Decimal('3000.00'))
    order.refresh_from_db()
    assert order.estado == Order.States.PAGADO_PARCIAL
    assert TransactionSelector.total_pending(order) == Decimal('3000.00')

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.ABONO, amount=Decimal('3000.00'))
    order.refresh_from_db()
    assert order.estado == Order.States.COMPLETADO
    assert TransactionSelector.total_pending(order) == Decimal('0')


@pytest.mark.django_db
def test_get_unpaid_items_excludes_paid_and_annulled():
    """Verifica que get_unpaid_items excluye items PAGADO y ANULADO."""
    tenant = Tenant.objects.create(slug='unpaid-items', name='Unpaid Items')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T13')
    product1 = _create_product(tenant=tenant, name='Item1', price='1000.00')
    product2 = _create_product(tenant=tenant, name='Item2', price='2000.00')
    product3 = _create_product(tenant=tenant, name='Item3', price='3000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    item1 = add_or_update_item_in_order(user=user_garzon, order=order, product=product1, cantidad=1)
    item2 = add_or_update_item_in_order(user=user_garzon, order=order, product=product2, cantidad=1)
    item3 = add_or_update_item_in_order(user=user_garzon, order=order, product=product3, cantidad=1)

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.PRODUCTOS, order_items=[item1])

    remove_item_from_order(user=user_garzon, item=item3)

    unpaid = OrderItemSelector.get_unpaid_items(order)

    assert unpaid.count() == 1
    assert unpaid.first() == item2


@pytest.mark.django_db
def test_get_paid_items_returns_only_paid():
    """Verifica que get_paid_items retorna solo items PAGADO."""
    tenant = Tenant.objects.create(slug='paid-items', name='Paid Items')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T14')
    product1 = _create_product(tenant=tenant, name='A', price='1000.00')
    product2 = _create_product(tenant=tenant, name='B', price='2000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    item1 = add_or_update_item_in_order(user=user_garzon, order=order, product=product1, cantidad=1)
    item2 = add_or_update_item_in_order(user=user_garzon, order=order, product=product2, cantidad=1)

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.PRODUCTOS, order_items=[item1])

    paid = OrderItemSelector.get_paid_items(order)

    assert paid.count() == 1
    assert paid.first() == item1


@pytest.mark.django_db
def test_items_paid_amount_returns_sum_of_product_transactions():
    """Verifica que items_paid_amount retorna la suma de transacciones PRODUCTOS."""
    tenant = Tenant.objects.create(slug='items-amount', name='Items Amount')
    user_cajero = _create_cajero_user(tenant)
    user_garzon = _create_garzon_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T15')
    product1 = _create_product(tenant=tenant, name='X', price='1500.00')
    product2 = _create_product(tenant=tenant, name='Y', price='2500.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    item1 = add_or_update_item_in_order(user=user_garzon, order=order, product=product1, cantidad=1)
    item2 = add_or_update_item_in_order(user=user_garzon, order=order, product=product2, cantidad=1)

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.PRODUCTOS, order_items=[item1])

    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.ABONO, amount=Decimal('500.00'))

    assert TransactionSelector.items_paid_amount(order) == Decimal('1500.00')
