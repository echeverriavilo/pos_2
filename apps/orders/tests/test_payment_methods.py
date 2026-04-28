from decimal import Decimal

import pytest

from apps.core.models import CustomUser, Membership, Role, Tenant
from apps.core.services.tenant import TenantService
from apps.orders.models import PaymentMethod, Order, Transaction
from apps.orders.services.payment import register_transaction, TransactionError
from apps.orders.services.cash_register import create_cash_register
from apps.orders.services.cash_session import open_cash_session


def _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=True, soporta_flujo_rapido=True):
    """Abre una sesión de caja para un tenant. Retorna la CashSession."""
    cr = create_cash_register(
        user=user, tenant=tenant, nombre='Caja Test',
        soporta_flujo_mesa=soporta_flujo_mesa, soporta_flujo_rapido=soporta_flujo_rapido,
    )
    return open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))


@pytest.fixture
def tenant(db):
    return TenantService.create_tenant(slug='test-payment-methods', name='Test Payment Methods')


@pytest.fixture
def tenant_b(db):
    return TenantService.create_tenant(slug='test-payment-methods-b', name='Test Payment Methods B')


@pytest.fixture
def user(db, tenant):
    from apps.core.models import CustomUser, Membership, Role
    user = CustomUser.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    role = Role.objects.filter(tenant=tenant, name='administrador').first()
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


@pytest.fixture
def order_with_items(db, tenant, user):
    from apps.orders.services.order import create_order, add_or_update_item_in_order, recalculate_total
    from apps.catalog.models import Product, Category
    
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    category = Category.objects.create(tenant=tenant, nombre='Test')
    product = Product.objects.create(
        tenant=tenant,
        category=category,
        nombre='Producto Test',
        precio_bruto=Decimal('10000'),
        is_active=True,
        stock_actual=Decimal('100')
    )
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
    recalculate_total(order)
    return order


class TestPaymentMethodSeed:
    def test_seed_creates_default_payment_methods(self, tenant):
        methods = PaymentMethod.objects.for_tenant(tenant).filter(activo=True)
        assert methods.count() == 4
        nombres = [m.nombre for m in methods]
        assert 'Efectivo' in nombres
        assert 'Tarjeta Débito' in nombres
        assert 'Tarjeta Crédito' in nombres
        assert 'Transferencia' in nombres

    def test_seed_payment_methods_are_ordered(self, tenant):
        methods = list(PaymentMethod.objects.for_tenant(tenant).all())
        assert methods[0].nombre == 'Efectivo'
        assert methods[1].nombre == 'Tarjeta Débito'
        assert methods[2].nombre == 'Tarjeta Crédito'
        assert methods[3].nombre == 'Transferencia'

    def test_payment_methods_are_tenant_isolated(self, tenant, tenant_b):
        methods_tenant_a = PaymentMethod.objects.for_tenant(tenant).count()
        methods_tenant_b = PaymentMethod.objects.for_tenant(tenant_b).count()
        assert methods_tenant_a == 4
        assert methods_tenant_b == 4
        
        method_a = PaymentMethod.objects.for_tenant(tenant).first()
        assert method_a.tenant == tenant
        assert method_a.tenant != tenant_b


class TestPaymentMethodModel:
    def test_create_payment_method_requires_tenant(self, tenant):
        method = PaymentMethod.objects.create(
            tenant=tenant,
            nombre='Test Method',
            activo=True,
            orden=10
        )
        assert method.tenant == tenant
        assert method.nombre == 'Test Method'
        assert method.activo is True
        assert method.orden == 10

    def test_payment_method_unique_nombre_per_tenant(self, tenant):
        PaymentMethod.objects.create(tenant=tenant, nombre='Unique Method', activo=True)
        with pytest.raises(Exception):
            PaymentMethod.objects.create(tenant=tenant, nombre='Unique Method', activo=True)

    def test_can_have_same_nombre_in_different_tenants(self, tenant, tenant_b):
        PaymentMethod.objects.create(tenant=tenant, nombre='Same Name', activo=True)
        method_b = PaymentMethod.objects.create(tenant=tenant_b, nombre='Same Name', activo=True)
        assert method_b.tenant == tenant_b


class TestTransactionWithPaymentMethod:
    def test_transaction_requires_payment_method(self, tenant, user, order_with_items):
        _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=False, soporta_flujo_rapido=True)
        payment_method = PaymentMethod.objects.for_tenant(tenant).first()
        transaction = register_transaction(
            user=user,
            tenant=tenant,
            order=order_with_items,
            payment_type=Transaction.PaymentType.TOTAL,
            payment_method=payment_method,
            tip_amount=Decimal('0'),
        )
        assert transaction.payment_method == payment_method
        assert transaction.tip_amount == Decimal('0')

    def test_transaction_requires_active_payment_method(self, tenant, user, order_with_items):
        _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=False, soporta_flujo_rapido=True)
        payment_method = PaymentMethod.objects.for_tenant(tenant).first()
        payment_method.activo = False
        payment_method.save()
        
        with pytest.raises(TransactionError, match='no está activo'):
            register_transaction(
                user=user,
                tenant=tenant,
                order=order_with_items,
                payment_type=Transaction.PaymentType.TOTAL,
                payment_method=payment_method,
            )

    def test_transaction_payment_method_must_belong_to_tenant(self, tenant, tenant_b, user, order_with_items):
        _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=False, soporta_flujo_rapido=True)
        payment_method_b = PaymentMethod.objects.for_tenant(tenant_b).first()
        
        with pytest.raises(TransactionError, match='debe pertenecer al tenant'):
            register_transaction(
                user=user,
                tenant=tenant,
                order=order_with_items,
                payment_type=Transaction.PaymentType.TOTAL,
                payment_method=payment_method_b,
            )

    def test_transaction_without_payment_method_raises_error(self, tenant, user, order_with_items):
        _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=False, soporta_flujo_rapido=True)
        with pytest.raises(TransactionError, match='método de pago es obligatorio'):
            register_transaction(
                user=user,
                tenant=tenant,
                order=order_with_items,
                payment_type=Transaction.PaymentType.TOTAL,
                payment_method=None,
            )

    def test_transaction_tip_amount_cannot_be_negative(self, tenant, user, order_with_items):
        _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=False, soporta_flujo_rapido=True)
        payment_method = PaymentMethod.objects.for_tenant(tenant).first()
        
        with pytest.raises(TransactionError, match='no puede ser negativo'):
            register_transaction(
                user=user,
                tenant=tenant,
                order=order_with_items,
                payment_type=Transaction.PaymentType.TOTAL,
                payment_method=payment_method,
                tip_amount=Decimal('-100'),
            )

    def test_transaction_tip_has_no_upper_limit(self, tenant, user, order_with_items):
        _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=False, soporta_flujo_rapido=True)
        payment_method = PaymentMethod.objects.for_tenant(tenant).first()
        
        transaction = register_transaction(
            user=user,
            tenant=tenant,
            order=order_with_items,
            payment_type=Transaction.PaymentType.TOTAL,
            payment_method=payment_method,
            tip_amount=Decimal('999999'),
        )
        assert transaction.tip_amount == Decimal('999999')


class TestTransactionSelectorWithTip:
    @pytest.fixture
    def order_with_transactions(self, db, tenant, user):
        from apps.orders.services.order import create_order, add_or_update_item_in_order, recalculate_total
        from apps.catalog.models import Product, Category
        
        _open_cash_session_for_tenant(user, tenant, soporta_flujo_mesa=False, soporta_flujo_rapido=True)

        order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
        category = Category.objects.create(tenant=tenant, nombre='Test')
        product = Product.objects.create(
            tenant=tenant,
            category=category,
            nombre='Producto Test',
            precio_bruto=Decimal('10000'),
            is_active=True,
            stock_actual=Decimal('100')
        )
        add_or_update_item_in_order(user=user, order=order, product=product, cantidad=2)
        recalculate_total(order)
        
        payment_method = PaymentMethod.objects.for_tenant(tenant).first()
        
        register_transaction(
            user=user,
            tenant=tenant,
            order=order,
            payment_type=Transaction.PaymentType.ABONO,
            amount=Decimal('5000'),
            payment_method=payment_method,
            tip_amount=Decimal('500'),
        )
        
        register_transaction(
            user=user,
            tenant=tenant,
            order=order,
            payment_type=Transaction.PaymentType.ABONO,
            amount=Decimal('5000'),
            payment_method=payment_method,
            tip_amount=Decimal('1000'),
        )
        
        return order

    def test_total_tip_paid_returns_sum_of_transaction_tips(self, order_with_transactions):
        from apps.orders.selectors.transaction import TransactionSelector
        total_tip = TransactionSelector.total_tip_paid(order_with_transactions)
        assert total_tip == Decimal('1500')

    def test_total_consumo_returns_order_total_bruto(self, order_with_transactions):
        from apps.orders.selectors.transaction import TransactionSelector
        total_consumo = TransactionSelector.total_cuenta(order_with_transactions)
        assert total_consumo == order_with_transactions.total_bruto
