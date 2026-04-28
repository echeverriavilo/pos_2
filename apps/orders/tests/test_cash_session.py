from decimal import Decimal

import pytest

from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission
from apps.core.services.tenant import TenantService
from apps.orders.models import (
    CashCloseDetail,
    CashMovement,
    CashRegister,
    CashSession,
    Order,
    PaymentMethod,
    Transaction,
)
from apps.orders.services.cash_register import (
    CashRegisterError,
    create_cash_register,
    toggle_cash_register,
    update_cash_register,
)
from apps.orders.services.cash_session import (
    CashMovementError,
    CashSessionError,
    close_cash_session,
    get_session_summary,
    open_cash_session,
    register_cash_movement,
)
from apps.orders.services.payment import TransactionError
from apps.orders.selectors.cash_register import CashRegisterSelector
from apps.orders.selectors.cash_session import CashSessionSelector
from apps.dining.models import DiningTable
from apps.orders.services import add_or_update_item_in_order, create_order, register_transaction
from apps.catalog.models import Category, Product


def _setup_tenant_with_admin(slug='caja-test', name='Caja Test'):
    """Crea un tenant y un usuario superusuario que bypasa permisos."""
    tenant = TenantService.create_tenant(slug=slug, name=name)
    user = CustomUser.objects.create_superuser(
        email=f'admin@{slug}.com',
        password='test123',
    )
    Membership.objects.create(user=user, tenant=tenant, role=Role.objects.filter(tenant=tenant, name='administrador').first())
    return tenant, user


def _create_product(*, tenant, name, price):
    category, _ = Category.objects.get_or_create(tenant=tenant, nombre='General')
    return Product.objects.create(
        tenant=tenant,
        category=category,
        nombre=name,
        precio_bruto=Decimal(price),
        es_inventariable=False,
        stock_actual=Decimal('100'),
    )


def _get_efectivo_pm(tenant):
    """Obtiene o crea el método de pago Efectivo para un tenant."""
    pm = PaymentMethod.objects.for_tenant(tenant).filter(nombre__iexact='Efectivo', activo=True).first()
    if pm is None:
        pm = PaymentMethod.objects.create(tenant=tenant, nombre='Efectivo', orden=1)
    return pm


# --- CashRegister tests ---

@pytest.mark.django_db
def test_create_cash_register_success():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(
        user=user, tenant=tenant, nombre='Caja Principal',
        soporta_flujo_mesa=True, soporta_flujo_rapido=True,
    )
    assert cr.tenant == tenant
    assert cr.nombre == 'Caja Principal'
    assert cr.soporta_flujo_mesa is True
    assert cr.soporta_flujo_rapido is True
    assert cr.activo is True


@pytest.mark.django_db
def test_create_cash_register_no_flows_fails():
    tenant, user = _setup_tenant_with_admin()
    with pytest.raises(CashRegisterError, match='al menos un flujo'):
        create_cash_register(
            user=user, tenant=tenant, nombre='Caja Sin Flujo',
            soporta_flujo_mesa=False, soporta_flujo_rapido=False,
        )


@pytest.mark.django_db
def test_create_cash_register_empty_name_fails():
    tenant, user = _setup_tenant_with_admin()
    with pytest.raises(CashRegisterError, match='nombre.*obligatorio'):
        create_cash_register(user=user, tenant=tenant, nombre='  ')


@pytest.mark.django_db
def test_multiple_cash_registers_per_tenant():
    tenant, user = _setup_tenant_with_admin()
    cr1 = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    cr2 = create_cash_register(user=user, tenant=tenant, nombre='Caja 2')
    assert cr1.pk != cr2.pk
    registers = CashRegisterSelector.list_cash_registers(tenant)
    assert registers.count() == 2


@pytest.mark.django_db
def test_toggle_cash_register_deactivate():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    toggle_cash_register(user=user, tenant=tenant, pk=cr.pk, activo=False)
    cr.refresh_from_db()
    assert cr.activo is False


@pytest.mark.django_db
def test_cannot_deactivate_register_with_open_session():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('5000'))
    with pytest.raises(CashRegisterError, match='sesión abierta'):
        toggle_cash_register(user=user, tenant=tenant, pk=cr.pk, activo=False)


@pytest.mark.django_db
def test_cash_register_tenant_isolation():
    tenant1, user1 = _setup_tenant_with_admin(slug='t1-isol', name='T1 Isol')
    tenant2, user2 = _setup_tenant_with_admin(slug='t2-isol', name='T2 Isol')
    create_cash_register(user=user1, tenant=tenant1, nombre='Caja T1')
    regs_t1 = CashRegisterSelector.list_cash_registers(tenant1)
    regs_t2 = CashRegisterSelector.list_cash_registers(tenant2)
    assert regs_t1.count() == 1
    assert regs_t2.count() == 0


# --- CashSession tests ---

@pytest.mark.django_db
def test_open_session_success():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('10000'))
    assert session.estado == CashSession.States.ABIERTA
    assert session.opened_by == user
    assert session.monto_apertura == Decimal('10000')
    assert session.cash_register == cr


@pytest.mark.django_db
def test_open_session_no_duplicate_per_register():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))
    with pytest.raises(CashSessionError, match='sesión abierta'):
        open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))


@pytest.mark.django_db
def test_open_session_inactive_register_fails():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    toggle_cash_register(user=user, tenant=tenant, pk=cr.pk, activo=False)
    with pytest.raises(CashSessionError, match='caja inactiva'):
        open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))


@pytest.mark.django_db
def test_open_session_negative_apertura_fails():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    with pytest.raises(CashSessionError, match='negativo'):
        open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('-100'))


@pytest.mark.django_db
def test_close_session_cuadratura_exacta():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('5000'))

    register_cash_movement(
        user=user, tenant=tenant, session_id=session.pk,
        tipo=CashMovement.MovementType.INGRESO, monto=Decimal('3000'), descripcion='Venta',
    )

    efectivo = _get_efectivo_pm(tenant)
    closed = close_cash_session(
        user=user, tenant=tenant, session_id=session.pk,
        payment_details=[{'payment_method_id': efectivo.pk, 'monto_declarado': '8000'}],
    )
    assert closed.estado == CashSession.States.CERRADA
    assert closed.closed_by == user
    assert closed.diferencia == Decimal('0')


@pytest.mark.django_db
def test_close_session_with_difference():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('5000'))

    register_cash_movement(
        user=user, tenant=tenant, session_id=session.pk,
        tipo=CashMovement.MovementType.INGRESO, monto=Decimal('3000'), descripcion='Venta',
    )

    efectivo = _get_efectivo_pm(tenant)
    closed = close_cash_session(
        user=user, tenant=tenant, session_id=session.pk,
        payment_details=[{'payment_method_id': efectivo.pk, 'monto_declarado': '7500', 'comentario': 'Faltante detectado'}],
        comentario_cierre='Faltante detectado',
    )
    assert closed.diferencia == Decimal('-500')


@pytest.mark.django_db
def test_cannot_reopen_closed_session():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))
    efectivo = _get_efectivo_pm(tenant)
    close_cash_session(
        user=user, tenant=tenant, session_id=session.pk,
        payment_details=[{'payment_method_id': efectivo.pk, 'monto_declarado': '0'}],
    )

    with pytest.raises(CashSessionError, match='cerrar sesiones abiertas'):
        close_cash_session(
            user=user, tenant=tenant, session_id=session.pk,
            payment_details=[{'payment_method_id': efectivo.pk, 'monto_declarado': '0'}],
        )

    new_session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))
    assert new_session.pk != session.pk


@pytest.mark.django_db
def test_cash_movement_manual():
    tenant, user = _setup_tenant_with_admin()
    efectivo = _get_efectivo_pm(tenant)
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('10000'))

    mov_egreso = register_cash_movement(
        user=user, tenant=tenant, session_id=session.pk,
        tipo=CashMovement.MovementType.EGRESO, monto=Decimal('2000'), descripcion='Retiro efectivo',
    )
    assert mov_egreso.tipo == CashMovement.MovementType.EGRESO
    assert mov_egreso.monto == Decimal('2000')
    assert mov_egreso.descripcion == 'Retiro efectivo'
    assert mov_egreso.payment_method == efectivo

    mov_ajuste = register_cash_movement(
        user=user, tenant=tenant, session_id=session.pk,
        tipo=CashMovement.MovementType.AJUSTE, monto=Decimal('500'), descripcion='Ajuste positivo',
        payment_method_id=efectivo.pk,
    )
    assert mov_ajuste.tipo == CashMovement.MovementType.AJUSTE
    assert mov_ajuste.payment_method == efectivo


@pytest.mark.django_db
def test_cash_movement_closed_session_fails():
    tenant, user = _setup_tenant_with_admin()
    efectivo = _get_efectivo_pm(tenant)
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))
    close_cash_session(
        user=user, tenant=tenant, session_id=session.pk,
        payment_details=[{'payment_method_id': efectivo.pk, 'monto_declarado': '0'}],
    )

    with pytest.raises(CashMovementError, match='sesiones abiertas'):
        register_cash_movement(
            user=user, tenant=tenant, session_id=session.pk,
            tipo=CashMovement.MovementType.INGRESO, monto=Decimal('100'), descripcion='Fallo',
        )


@pytest.mark.django_db
def test_cash_movement_negative_amount_fails():
    tenant, user = _setup_tenant_with_admin()
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    with pytest.raises(CashMovementError, match='mayor que cero'):
        register_cash_movement(
            user=user, tenant=tenant, session_id=session.pk,
            tipo=CashMovement.MovementType.INGRESO, monto=Decimal('-100'), descripcion='Negativo',
        )


@pytest.mark.django_db
def test_session_summary_calculations():
    tenant, user = _setup_tenant_with_admin()
    efectivo = _get_efectivo_pm(tenant)
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('10000'))

    register_cash_movement(
        user=user, tenant=tenant, session_id=session.pk,
        tipo=CashMovement.MovementType.INGRESO, monto=Decimal('5000'), descripcion='Ventas',
    )
    register_cash_movement(
        user=user, tenant=tenant, session_id=session.pk,
        tipo=CashMovement.MovementType.EGRESO, monto=Decimal('2000'), descripcion='Retiro',
    )
    register_cash_movement(
        user=user, tenant=tenant, session_id=session.pk,
        tipo=CashMovement.MovementType.AJUSTE, monto=Decimal('300'), descripcion='Ajuste',
        payment_method_id=efectivo.pk,
    )

    summary = get_session_summary(session)
    assert summary['monto_apertura'] == Decimal('10000')
    assert summary['total_ingresos'] == Decimal('5000')
    assert summary['total_egresos'] == Decimal('2000')
    assert summary['total_ajustes'] == Decimal('300')
    assert summary['total_esperado'] == Decimal('13300')


@pytest.mark.django_db
def test_close_session_permission_required():
    tenant, admin_user = _setup_tenant_with_admin(slug='perm-test', name='Perm Test')
    efectivo = _get_efectivo_pm(tenant)
    cr = create_cash_register(user=admin_user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=admin_user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    other_user = CustomUser.objects.create_user(email='noperm@perm-test.com', password='test123')
    garzon_role = Role.objects.filter(tenant=tenant, name='garzón').first()
    Membership.objects.create(user=other_user, tenant=tenant, role=garzon_role)

    from apps.core.services.auth import AuthorizationError
    with pytest.raises(AuthorizationError):
        close_cash_session(
            user=other_user, tenant=tenant, session_id=session.pk,
            payment_details=[{'payment_method_id': efectivo.pk, 'monto_declarado': '0'}],
        )


@pytest.mark.django_db
def test_session_tenant_isolation():
    tenant1, user1 = _setup_tenant_with_admin(slug='t1-iso', name='T1 Iso')
    tenant2, user2 = _setup_tenant_with_admin(slug='t2-iso', name='T2 Iso')
    cr1 = create_cash_register(user=user1, tenant=tenant1, nombre='Caja T1')
    cr2 = create_cash_register(user=user2, tenant=tenant2, nombre='Caja T2')

    session1 = open_cash_session(user=user1, tenant=tenant1, cash_register_id=cr1.pk, monto_apertura=Decimal('0'))
    session2 = open_cash_session(user=user2, tenant=tenant2, cash_register_id=cr2.pk, monto_apertura=Decimal('0'))

    register_cash_movement(
        user=user1, tenant=tenant1, session_id=session1.pk,
        tipo=CashMovement.MovementType.INGRESO, monto=Decimal('5000'), descripcion='Venta T1',
    )

    summary1 = get_session_summary(session1)
    summary2 = get_session_summary(session2)
    assert summary1['total_ingresos'] == Decimal('5000')
    assert summary2['total_ingresos'] == Decimal('0')


# --- Integration: payment requires open session ---

@pytest.mark.django_db
def test_payment_requires_open_session():
    tenant, user = _setup_tenant_with_admin(slug='pago-sin-ses', name='Pago Sin Sesion')
    product = _create_product(tenant=tenant, name='Producto', price='5000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
    payment_method = PaymentMethod.objects.for_tenant(tenant).filter(activo=True).first()

    with pytest.raises(TransactionError, match='sesión de caja abierta'):
        register_transaction(
            user=user, tenant=tenant, order=order,
            payment_type=Transaction.PaymentType.TOTAL,
            payment_method=payment_method,
        )


@pytest.mark.django_db
def test_payment_creates_cash_movement():
    tenant, user = _setup_tenant_with_admin(slug='pago-con-ses', name='Pago Con Sesion')
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1', soporta_flujo_rapido=True)
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    product = _create_product(tenant=tenant, name='Producto', price='5000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
    payment_method = PaymentMethod.objects.for_tenant(tenant).filter(activo=True).first()

    transaction_record = register_transaction(
        user=user, tenant=tenant, order=order,
        payment_type=Transaction.PaymentType.TOTAL,
        payment_method=payment_method,
    )

    movements = CashMovement.objects.filter(cash_session=session)
    assert movements.count() == 1
    mov = movements.first()
    assert mov.tipo == CashMovement.MovementType.INGRESO
    assert mov.transaction == transaction_record
    assert mov.monto == Decimal('5000.00')


@pytest.mark.django_db
def test_payment_uses_compatible_session_for_mesa():
    tenant, user = _setup_tenant_with_admin(slug='pago-mesa-ses', name='Pago Mesa Sesion')
    cr_mesa = create_cash_register(user=user, tenant=tenant, nombre='Caja Mesa', soporta_flujo_mesa=True, soporta_flujo_rapido=False)
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr_mesa.pk, monto_apertura=Decimal('0'))

    table = DiningTable.objects.create(tenant=tenant, numero='M1', estado=DiningTable.States.PAGANDO)
    product = _create_product(tenant=tenant, name='Plato', price='8000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
    payment_method = PaymentMethod.objects.for_tenant(tenant).filter(activo=True).first()

    transaction_record = register_transaction(
        user=user, tenant=tenant, order=order,
        payment_type=Transaction.PaymentType.TOTAL,
        payment_method=payment_method,
    )

    movements = CashMovement.objects.filter(cash_session=session)
    assert movements.count() == 1
    assert movements.first().transaction == transaction_record


@pytest.mark.django_db
def test_get_active_session_for_order():
    tenant, user = _setup_tenant_with_admin(slug='sesion-orden2', name='Sesion Orden2')
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja Mixta')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    product = _create_product(tenant=tenant, name='Producto', price='3000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)

    found_session = CashSessionSelector.get_active_session_for_order(tenant, order)
    assert found_session is not None
    assert found_session.pk == session.pk


@pytest.mark.django_db
def test_get_active_session_for_order_returns_none_when_no_session():
    tenant, user = _setup_tenant_with_admin(slug='sin-sesion2', name='Sin Sesion2')
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')

    product = _create_product(tenant=tenant, name='Producto', price='3000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)

    found_session = CashSessionSelector.get_active_session_for_order(tenant, order)
    assert found_session is None


# --- Correcciones pendientes (bug fix, cuadratura, UI) ---

@pytest.mark.django_db
def test_cash_movement_includes_tip_amount():
    """El CashMovement de pago debe incluir transaction_amount + tip_amount."""
    tenant, user = _setup_tenant_with_admin(slug='propina-test', name='Propina Test')
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1', soporta_flujo_rapido=True)
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    product = _create_product(tenant=tenant, name='Producto', price='5000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
    payment_method = PaymentMethod.objects.for_tenant(tenant).filter(activo=True).first()

    transaction_record = register_transaction(
        user=user, tenant=tenant, order=order,
        payment_type=Transaction.PaymentType.TOTAL,
        payment_method=payment_method,
        tip_amount=Decimal('500'),
    )

    movements = CashMovement.objects.filter(cash_session=session)
    assert movements.count() == 1
    mov = movements.first()
    assert mov.monto == Decimal('5500.00')


@pytest.mark.django_db
def test_close_session_creates_cash_close_details():
    """El cierre con payment_details debe crear CashCloseDetail por medio de pago."""
    tenant, user = _setup_tenant_with_admin(slug='detail-test', name='Detail Test')
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    payment_method = PaymentMethod.objects.for_tenant(tenant).filter(activo=True).first()
    product = _create_product(tenant=tenant, name='Producto', price='3000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)

    register_transaction(
        user=user, tenant=tenant, order=order,
        payment_type=Transaction.PaymentType.TOTAL,
        payment_method=payment_method,
    )

    close_cash_session(
        user=user, tenant=tenant, session_id=session.pk,
        payment_details=[{'payment_method_id': payment_method.pk, 'monto_declarado': '3000'}],
        comentario_cierre='',
    )

    details = CashCloseDetail.objects.filter(cash_session=session)
    assert details.count() == 1
    detail = details.first()
    assert detail.payment_method == payment_method
    assert detail.monto_sistema == Decimal('3000')
    assert detail.monto_declarado == Decimal('3000')
    assert detail.diferencia == Decimal('0')


@pytest.mark.django_db
def test_close_session_requires_comment_on_difference():
    """El comentario es obligatorio cuando hay diferencia en la cuadratura."""
    tenant, user = _setup_tenant_with_admin(slug='diff-comment', name='Diff Comment')
    efectivo = _get_efectivo_pm(tenant)
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    with pytest.raises(CashSessionError, match='Debe explicar'):
        close_cash_session(
            user=user, tenant=tenant, session_id=session.pk,
            payment_details=[{'payment_method_id': efectivo.pk, 'monto_declarado': '100'}],
        )


@pytest.mark.django_db
def test_close_session_comment_optional_when_balanced():
    """El comentario es opcional cuando la caja cuadra exactamente."""
    tenant, user = _setup_tenant_with_admin(slug='balanced', name='Balanced')
    efectivo = _get_efectivo_pm(tenant)
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('5000'))

    register_cash_movement(
        user=user, tenant=tenant, session_id=session.pk,
        tipo=CashMovement.MovementType.INGRESO, monto=Decimal('3000'), descripcion='Venta',
    )

    closed = close_cash_session(
        user=user, tenant=tenant, session_id=session.pk,
        payment_details=[{'payment_method_id': efectivo.pk, 'monto_declarado': '8000'}],
        comentario_cierre='',
    )
    assert closed.diferencia == Decimal('0')


@pytest.mark.django_db
def test_register_cash_movement_requires_description_when_manual():
    """La descripción es obligatoria para movimientos manuales."""
    tenant, user = _setup_tenant_with_admin(slug='manual-desc', name='Manual Desc')
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1')
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    with pytest.raises(CashMovementError, match='descripción.*obligatoria'):
        register_cash_movement(
            user=user, tenant=tenant, session_id=session.pk,
            tipo=CashMovement.MovementType.INGRESO, monto=Decimal('100'), descripcion='',
        )


@pytest.mark.django_db
def test_get_session_payment_breakdown():
    """El selector debe retornar el desglose correcto por medio de pago."""
    tenant, user = _setup_tenant_with_admin(slug='breakdown', name='Breakdown')
    cr = create_cash_register(user=user, tenant=tenant, nombre='Caja 1', soporta_flujo_rapido=True)
    session = open_cash_session(user=user, tenant=tenant, cash_register_id=cr.pk, monto_apertura=Decimal('0'))

    payment_methods = list(PaymentMethod.objects.for_tenant(tenant).filter(activo=True)[:2])
    if len(payment_methods) < 2:
        # Crear un segundo método de pago si no existe
        payment_methods.append(PaymentMethod.objects.create(tenant=tenant, nombre='Otro'))

    product = _create_product(tenant=tenant, name='Producto', price='4000.00')
    order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
    add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)

    register_transaction(
        user=user, tenant=tenant, order=order,
        payment_type=Transaction.PaymentType.TOTAL,
        payment_method=payment_methods[0],
        tip_amount=Decimal('200'),
    )

    breakdown = CashSessionSelector.get_session_payment_breakdown(session)
    assert breakdown[payment_methods[0].pk] == Decimal('4200')
    assert payment_methods[1].pk not in breakdown