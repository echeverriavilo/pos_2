"""Tests para las correcciones de la 2da ronda del Hito 11."""
import pytest
from decimal import Decimal

from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission, Tenant
from apps.dining.models import DiningTable
from apps.dining.services.table import DiningTableService, DiningTableError
from apps.orders.models import Order, OrderItem, Transaction, PaymentMethod
from apps.orders.services.order import (
    add_or_update_item_in_order,
    create_order_for_table,
    recalculate_total,
    remove_item_from_order,
)
from apps.orders.services.payment import register_transaction, TransactionError
from apps.orders.selectors.order_item import OrderItemSelector
from apps.orders.selectors.transaction import TransactionSelector
from apps.orders.services.cash_register import create_cash_register
from apps.orders.services.cash_session import open_cash_session


def _create_garzon_user(tenant):
    user = CustomUser.objects.create_user(email=f'garzon@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='garzon')
    for perm_codename in ['create_order', 'add_item', 'remove_item', 'manage_tables']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        RolePermission.objects.get_or_create(role=role, permission=perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


def _create_cajero_user(tenant):
    user = CustomUser.objects.create_user(email=f'cajero@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='cajero')
    for perm_codename in ['register_payment', 'manage_tables', 'manage_cash_registers', 'open_cash_session']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        RolePermission.objects.get_or_create(role=role, permission=perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


def _create_product(tenant, name, price):
    from apps.catalog.models import Category, Product
    category, _ = Category.objects.get_or_create(tenant=tenant, nombre='Test')
    return Product.objects.create(
        tenant=tenant,
        category=category,
        nombre=name,
        precio_bruto=Decimal(price),
        es_inventariable=False,
    )


def _create_payment_method(tenant):
    return PaymentMethod.objects.create(tenant=tenant, nombre='Efectivo', orden=0, activo=True)


def _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=True, soporta_flujo_rapido=True):
    """Abre una sesión de caja para un tenant. Retorna la CashSession."""
    cr = create_cash_register(
        user=user, tenant=tenant, nombre='Caja Test',
        soporta_flujo_mesa=soporta_flujo_mesa, soporta_flujo_rapido=soporta_flujo_rapido,
    )
    return open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))


@pytest.mark.django_db
def test_add_item_after_paid_creates_new_item():
    """Verifica que agregar un producto pagado crea un nuevo item en vez de modificar el existente."""
    tenant = Tenant.objects.create(slug='test-add-paid', name='Test Add Paid')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T1')
    product = _create_product(tenant=tenant, name='Cerveza', price='1000.00')
    order = create_order_for_table(user=user_garzon, table=table)
    payment_method = _create_payment_method(tenant)
    _open_cash_session_for_tenant(user_cajero, tenant, soporta_flujo_mesa=True, soporta_flujo_rapido=False)
    
    item1 = add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=3)
    assert item1.cantidad == 3
    
    # Pagar el item completo
    register_transaction(user=user_cajero, tenant=tenant, order=order, payment_type=Transaction.PaymentType.PRODUCTOS, order_items=[item1], payment_method=payment_method)
    item1.refresh_from_db()
    assert item1.estado == OrderItem.States.PAGADO
    
    # Agregar el mismo producto de nuevo
    item2 = add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=2)
    
    assert item2.pk != item1.pk
    assert item2.cantidad == 2
    assert item2.estado != OrderItem.States.PAGADO
    assert item1.cantidad == 3


@pytest.mark.django_db
def test_split_item_partial_quantity_payment():
    """Verifica que pagar una cantidad parcial de un item crea un item residual."""
    tenant = Tenant.objects.create(slug='test-split', name='Test Split')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T2')
    product = _create_product(tenant=tenant, name='Cerveza', price='1000.00')
    order = create_order_for_table(user=user_garzon, table=table)
    payment_method = _create_payment_method(tenant)
    _open_cash_session_for_tenant(user_cajero, tenant, soporta_flujo_mesa=True, soporta_flujo_rapido=False)
    
    item = add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=5)
    assert item.cantidad == 5
    
    # Pagar solo 3 de las 5 cervezas
    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.PRODUCTOS,
        order_items=[item],
        cantidades={str(item.pk): 3},
        payment_method=payment_method,
    )
    
    item.refresh_from_db()
    assert item.cantidad == 3
    assert item.estado == OrderItem.States.PAGADO
    
    residual = OrderItem.objects.filter(order=order, product=product).exclude(pk=item.pk).first()
    assert residual is not None
    assert residual.cantidad == 2
    assert residual.estado != OrderItem.States.PAGADO
    
    assert TransactionSelector.total_consumo_paid(order) == Decimal('3000.00')


@pytest.mark.django_db
def test_release_table_without_items():
    """Verifica que se puede liberar una mesa OCUPADA sin items."""
    tenant = Tenant.objects.create(slug='test-release', name='Test Release')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T3')
    
    order = create_order_for_table(user=user_garzon, table=table)
    table.estado = DiningTable.States.OCUPADA
    table.save(update_fields=['estado'])
    
    assert order.items.count() == 0
    
    released_table = DiningTableService.release_table(user=user_cajero, table=table)
    
    assert released_table.estado == DiningTable.States.DISPONIBLE


@pytest.mark.django_db
def test_release_table_with_all_annulled_items():
    """Verifica que se puede liberar una mesa con items solo anulados."""
    tenant = Tenant.objects.create(slug='test-release-annulled', name='Test Release Annulled')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T4')
    product = _create_product(tenant=tenant, name='Item', price='500.00')
    
    order = create_order_for_table(user=user_garzon, table=table)
    item = add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=1)
    
    remove_item_from_order(user=user_garzon, item=item)
    
    table.estado = DiningTable.States.OCUPADA
    table.save(update_fields=['estado'])
    
    released_table = DiningTableService.release_table(user=user_cajero, table=table)
    
    assert released_table.estado == DiningTable.States.DISPONIBLE
    order.refresh_from_db()
    assert order.estado == Order.States.ANULADO


@pytest.mark.django_db
def test_release_table_with_active_items_fails():
    """Verifica que no se puede liberar una mesa con items activos."""
    tenant = Tenant.objects.create(slug='test-release-active', name='Test Release Active')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T5')
    product = _create_product(tenant=tenant, name='Item', price='500.00')
    
    order = create_order_for_table(user=user_garzon, table=table)
    add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=1)
    
    table.estado = DiningTable.States.OCUPADA
    table.save(update_fields=['estado'])
    
    with pytest.raises(DiningTableError, match='No se puede liberar'):
        DiningTableService.release_table(user=user_cajero, table=table)


@pytest.mark.django_db
def test_partial_payment_by_quantity_updates_pending():
    """Verifica que el pago parcial por cantidad actualiza correctamente el pendiente."""
    tenant = Tenant.objects.create(slug='test-partial-qty', name='Test Partial Qty')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T6')
    product = _create_product(tenant=tenant, name='Pizza', price='2000.00')
    order = create_order_for_table(user=user_garzon, table=table)
    payment_method = _create_payment_method(tenant)
    _open_cash_session_for_tenant(user_cajero, tenant, soporta_flujo_mesa=True, soporta_flujo_rapido=False)
    
    item = add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=4)
    assert order.total_bruto == Decimal('8000.00')
    
    # Pagar 2 de 4 pizzas
    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.PRODUCTOS,
        order_items=[item],
        cantidades={str(item.pk): 2},
        payment_method=payment_method,
    )
    
    order.refresh_from_db()
    assert TransactionSelector.total_consumo_paid(order) == Decimal('4000.00')
    assert TransactionSelector.total_pending(order) == Decimal('4000.00')
    assert order.estado == Order.States.PAGADO_PARCIAL


@pytest.mark.django_db
def test_unpaid_items_excludes_split_residual():
    """Verifica que get_unpaid_items retorna el item residual tras un split."""
    tenant = Tenant.objects.create(slug='test-unpaid-split', name='Test Unpaid Split')
    user_garzon = _create_garzon_user(tenant)
    user_cajero = _create_cajero_user(tenant)
    table = DiningTable.objects.create(tenant=tenant, numero='T7')
    product = _create_product(tenant=tenant, name='Item', price='1000.00')
    order = create_order_for_table(user=user_garzon, table=table)
    payment_method = _create_payment_method(tenant)
    _open_cash_session_for_tenant(user_cajero, tenant, soporta_flujo_mesa=True, soporta_flujo_rapido=False)
    
    item = add_or_update_item_in_order(user=user_garzon, order=order, product=product, cantidad=3)
    
    register_transaction(
        user=user_cajero,
        tenant=tenant,
        order=order,
        payment_type=Transaction.PaymentType.PRODUCTOS,
        order_items=[item],
        cantidades={str(item.pk): 2},
        payment_method=payment_method,
    )
    
    unpaid = OrderItemSelector.get_unpaid_items(order)
    assert unpaid.count() == 1
    assert unpaid.first().cantidad == 1
