from decimal import Decimal

import pytest

from apps.catalog.models import Category, Product, StockMovement
from apps.core.models import CustomUser, Membership, Permission, Role, Tenant
from apps.dining.models import DiningTable
from apps.orders.models import Order, OrderItem, Transaction, TransactionItem
from apps.orders.selectors import TransactionSelector
from apps.orders.services import TransactionError, add_item, create_order, register_transaction


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
    role.permissions.add(perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


def _create_garzon_user(tenant):
    user = CustomUser.objects.create_user(email=f'garzon@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='garzon')
    for perm_codename in ['create_order', 'add_item', 'manage_tables']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        role.permissions.add(perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


@pytest.mark.django_db
def test_register_total_payment_completes_table_order_and_releases_table():
    tenant = Tenant.objects.create(slug='mesa-pagos', name='Mesa Pagos')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='11', estado=DiningTable.States.PAGANDO)
    product = _create_product(tenant=tenant, name='Plato', price='3500.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_item(user=user_garzon, order=order, product=product, cantidad=2)

    transaction_record = register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.TOTAL,
    )

    order.refresh_from_db()
    table.refresh_from_db()
    assert transaction_record.monto == Decimal('7000.00')
    assert order.estado == Order.States.COMPLETADO
    assert table.estado == DiningTable.States.DISPONIBLE
    assert TransactionSelector.total_paid(order) == Decimal('7000.00')
    assert TransactionSelector.total_pending(order) == Decimal('0.00')


@pytest.mark.django_db
def test_register_partial_payment_sets_partial_state():
    tenant = Tenant.objects.create(slug='abono-parcial', name='Abono Parcial')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='12')
    product = _create_product(tenant=tenant, name='Jugo', price='2500.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_item(user=user_garzon, order=order, product=product, cantidad=2)

    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.ABONO,
        amount=Decimal('1000.00'),
    )

    order.refresh_from_db()
    assert order.estado == Order.States.PAGADO_PARCIAL
    assert TransactionSelector.total_paid(order) == Decimal('1000.00')
    assert TransactionSelector.total_pending(order) == Decimal('4000.00')
    assert order.items.filter(estado=OrderItem.States.PAGADO).count() == 0


@pytest.mark.django_db
def test_product_payment_marks_only_selected_items_as_paid():
    tenant = Tenant.objects.create(slug='productos', name='Productos')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='13')
    product = _create_product(tenant=tenant, name='Postre', price='1800.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    first_item = add_item(user=user_garzon, order=order, product=product, cantidad=1)
    second_item = add_item(user=user_garzon, order=order, product=product, cantidad=2)

    transaction_record = register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.PRODUCTOS,
        order_items=[first_item],
    )

    first_item.refresh_from_db()
    second_item.refresh_from_db()
    order.refresh_from_db()
    transaction_item = TransactionItem.objects.get(transaction=transaction_record, order_item=first_item)
    assert transaction_item.tenant == tenant
    assert transaction_record.monto == Decimal('1800.00')
    assert first_item.estado == OrderItem.States.PAGADO
    assert second_item.estado != OrderItem.States.PAGADO
    assert order.estado == Order.States.PAGADO_PARCIAL


@pytest.mark.django_db
def test_product_payment_is_blocked_after_abono():
    tenant = Tenant.objects.create(slug='bloqueo-productos', name='Bloqueo Productos')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='14')
    product = _create_product(tenant=tenant, name='Cafe', price='1500.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    item = add_item(user=user_garzon, order=order, product=product, cantidad=2)
    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.ABONO,
        amount=Decimal('500.00'),
    )

    with pytest.raises(TransactionError):
        register_transaction(
            user=user_cajero,
            tenant=tenant,
            order=order,
            payment_type=Transaction.PaymentType.PRODUCTOS,
            order_items=[item],
        )


@pytest.mark.django_db
def test_quick_flow_full_first_payment_confirms_and_discounts_inventory():
    tenant = Tenant.objects.create(slug='rapido-pago-total', name='Rapido Pago Total')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    product = _create_product(
        tenant=tenant,
        name='Sandwich',
        price='4200.00',
        inventariable=True,
        stock='10.00',
    )
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    item = add_item(user=user_garzon, order=order, product=product, cantidad=2)

    transaction_record = register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.TOTAL,
    )

    order.refresh_from_db()
    item.refresh_from_db()
    product.refresh_from_db()
    assert transaction_record.monto == Decimal('8400.00')
    assert order.estado == Order.States.CONFIRMADO
    assert item.estado == OrderItem.States.PREPARACION
    assert product.stock_actual == Decimal('8.00')
    assert StockMovement.objects.filter(product=product, tipo=StockMovement.Types.VENTA).count() == 1


@pytest.mark.django_db
def test_payment_cannot_exceed_pending_total():
    tenant = Tenant.objects.create(slug='sobrepago', name='Sobrepago')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='15')
    product = _create_product(tenant=tenant, name='Sopa', price='2200.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_item(user=user_garzon, order=order, product=product, cantidad=1)

    with pytest.raises(TransactionError):
        register_transaction(
            user=user_cajero,
            tenant=tenant,
            order=order,
            payment_type=Transaction.PaymentType.ABONO,
            amount=Decimal('3000.00'),
        )


@pytest.mark.django_db
def test_paid_item_becomes_immutable():
    tenant = Tenant.objects.create(slug='item-inmutable', name='Item Inmutable')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='16')
    product = _create_product(tenant=tenant, name='Torta', price='1900.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    item = add_item(user=user_garzon, order=order, product=product, cantidad=1)
    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.PRODUCTOS,
        order_items=[item],
    )

    item.refresh_from_db()
    item.cantidad = 2
    with pytest.raises(ValueError):
        item.save(update_fields=['cantidad'])


@pytest.mark.django_db
def test_multiple_partial_payments_accumulate():
    tenant = Tenant.objects.create(slug='multiplos', name='Multiplos')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='17')
    product = _create_product(tenant=tenant, name='Pizza', price='5000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_item(user=user_garzon, order=order, product=product, cantidad=1)

    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.ABONO,
        amount=Decimal('2000.00'),
    )
    order.refresh_from_db()
    assert order.estado == Order.States.PAGADO_PARCIAL
    assert TransactionSelector.total_paid(order) == Decimal('2000.00')

    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.ABONO,
        amount=Decimal('2500.00'),
    )
    order.refresh_from_db()
    assert order.estado == Order.States.PAGADO_PARCIAL
    assert TransactionSelector.total_paid(order) == Decimal('4500.00')

    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.ABONO,
        amount=Decimal('500.00'),
    )
    order.refresh_from_db()
    assert order.estado == Order.States.COMPLETADO
    assert TransactionSelector.total_paid(order) == Decimal('5000.00')
    assert TransactionSelector.total_pending(order) == Decimal('0.00')


@pytest.mark.django_db
def test_product_payment_blocked_in_quick_flow():
    tenant = Tenant.objects.create(slug='rapido-bloq', name='Rapido Bloqueado')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    product = _create_product(tenant=tenant, name='Burrito', price='3200.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    item = add_item(user=user_garzon, order=order, product=product, cantidad=1)

    with pytest.raises(TransactionError):
        register_transaction(
            user=user_cajero,
            tenant=tenant,
            order=order,
            payment_type=Transaction.PaymentType.PRODUCTOS,
            order_items=[item],
        )


@pytest.mark.django_db
def test_total_payment_direct_from_open_completes_immediately():
    tenant = Tenant.objects.create(slug='directo', name='Directo')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='18')
    product = _create_product(tenant=tenant, name='Ensalada', price='2800.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_item(user=user_garzon, order=order, product=product, cantidad=1)

    assert order.estado == Order.States.ABIERTO
    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.TOTAL,
    )

    order.refresh_from_db()
    assert order.estado == Order.States.COMPLETADO
    table.refresh_from_db()
    assert table.estado == DiningTable.States.DISPONIBLE


@pytest.mark.django_db
def test_quick_flow_partial_payment_stays_in_partial_state():
    tenant = Tenant.objects.create(slug='rapido-parcial', name='Rapido Parcial')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    product = _create_product(tenant=tenant, name='Taco', price='2000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    add_item(user=user_garzon, order=order, product=product, cantidad=2)

    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.ABONO,
        amount=Decimal('2000.00'),
    )

    order.refresh_from_db()
    assert order.estado == Order.States.PAGADO_PARCIAL
    assert product.stock_actual == Decimal('20.00')


@pytest.mark.django_db
def test_multitenancy_isolation_in_transactions():
    tenant_a = Tenant.objects.create(slug='tenant-a-pago', name='Tenant A Pago')
    tenant_b = Tenant.objects.create(slug='tenant-b-pago', name='Tenant B Pago')
    user_garzon_a = _create_garzon_user(tenant_a)
    user_garzon_b = _create_garzon_user(tenant_b)
    user_cajero_a = _create_cajero_user(tenant_a)

    table_a = DiningTable.objects.create(tenant=tenant_a, numero='19')
    table_b = DiningTable.objects.create(tenant=tenant_b, numero='20')

    product_a = _create_product(tenant=tenant_a, name='Producto A', price='1500.00')
    product_b = _create_product(tenant=tenant_b, name='Producto B', price='1500.00')

    order_a = create_order(user=user_garzon_a, tenant=tenant_a, tipo_flujo=Order.Flow.MESA, table=table_a)
    order_b = create_order(user=user_garzon_b, tenant=tenant_b, tipo_flujo=Order.Flow.MESA, table=table_b)

    add_item(user=user_garzon_a, order=order_a, product=product_a, cantidad=1)
    add_item(user=user_garzon_b, order=order_b, product=product_b, cantidad=1)

    register_transaction(
        user=user_cajero_a,
        tenant=tenant_a,
        order=order_a,
        payment_type=Transaction.PaymentType.TOTAL,
    )

    order_a.refresh_from_db()
    order_b.refresh_from_db()

    assert order_a.estado == Order.States.COMPLETADO
    assert order_b.estado == Order.States.ABIERTO
    assert TransactionSelector.total_paid(order_a) == Decimal('1500.00')
    assert TransactionSelector.total_paid(order_b) == Decimal('0.00')


@pytest.mark.django_db
def test_cannot_pay_completed_or_cancelled_order():
    tenant = Tenant.objects.create(slug='cerrado', name='Cerrado')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='21')
    product = _create_product(tenant=tenant, name='Arepa', price='1200.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_item(user=user_garzon, order=order, product=product, cantidad=1)

    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.TOTAL,
    )

    order.refresh_from_db()
    assert order.estado == Order.States.COMPLETADO

    with pytest.raises(TransactionError):
        register_transaction(
            user=user_cajero,
            tenant=tenant,
            order=order,
            payment_type=Transaction.PaymentType.ABONO,
            amount=Decimal('100.00'),
        )


@pytest.mark.django_db
def test_total_paid_never_exceeds_total_bruto():
    tenant = Tenant.objects.create(slug='invariante', name='Invariante')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='22')
    product = _create_product(tenant=tenant, name='Caldo', price='1000.00')
    order = create_order(user=user_garzon, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_item(user=user_garzon, order=order, product=product, cantidad=1)

    assert TransactionSelector.total_paid(order) == Decimal('0.00')
    assert TransactionSelector.total_pending(order) == Decimal('1000.00')

    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.TOTAL,
    )

    assert TransactionSelector.total_paid(order) == Decimal('1000.00')
    assert TransactionSelector.total_paid(order) <= order.total_bruto