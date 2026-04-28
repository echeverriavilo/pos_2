from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.core.constants.actions import SystemActions
from apps.core.services.auth import validate_tenant_access, validate_role_permission
from apps.orders.models import CashCloseDetail, CashMovement, CashRegister, CashSession, PaymentMethod
from apps.orders.selectors.cash_session import CashSessionSelector


class CashSessionError(Exception):
    pass


class CashMovementError(Exception):
    pass


def open_cash_session(*, user, tenant, cash_register_id, monto_apertura=Decimal('0')):
    """Abre una nueva sesión de caja para un turno.

    Restricciones:
    - No se puede abrir una sesión si ya existe una abierta para la misma caja.
    - La caja debe estar activa.
    - Se requiere permiso open_cash_session.

    Parámetros:
    - user: usuario que abre la sesión.
    - tenant: tenant de la operación.
    - cash_register_id: id de la caja.
    - monto_apertura: monto inicial en caja (default 0).

    Retorno:
    - CashSession creada.
    """
    validate_tenant_access(user, tenant)
    validate_role_permission(user, SystemActions.OPEN_CASH_SESSION)

    if monto_apertura < Decimal('0'):
        raise CashSessionError('El monto de apertura no puede ser negativo.')

    cash_register = CashRegister.objects.for_tenant(tenant).get(pk=cash_register_id)

    if not cash_register.activo:
        raise CashSessionError('No se puede abrir una sesión en una caja inactiva.')

    existing_session = CashSession.objects.for_tenant(tenant).filter(
        cash_register=cash_register,
        estado=CashSession.States.ABIERTA,
    ).first()
    if existing_session:
        raise CashSessionError('Ya existe una sesión abierta para esta caja.')

    with transaction.atomic():
        session = CashSession.objects.create(
            tenant=tenant,
            cash_register=cash_register,
            opened_by=user,
            estado=CashSession.States.ABIERTA,
            monto_apertura=Decimal(monto_apertura),
        )
    return session


def close_cash_session(*, user, tenant, session_id, payment_details, comentario_cierre=''):
    """Cierra una sesión de caja con cuadratura por medio de pago.

    Calcula el desglose esperado por medio de pago, registra las diferencias
    declaradas y la diferencia general, y marca la sesión como cerrada.
    Crea CashCloseDetail por cada medio de pago declarado.

    Parámetros:
    - user: usuario que cierra la sesión.
    - tenant: tenant de la operación.
    - session_id: id de la sesión.
    - payment_details: lista de dicts con payment_method_id, monto_declarado y comentario.
    - comentario_cierre: comentario general opcional de la sesión.

    Retorno:
    - CashSession cerrada.
    """
    validate_tenant_access(user, tenant)
    validate_role_permission(user, SystemActions.CLOSE_CASH_SESSION)

    if not payment_details:
        raise CashSessionError('Debe declarar al menos un medio de pago para cerrar la caja.')

    with transaction.atomic():
        session = CashSession.objects.select_for_update().get(pk=session_id)

        if session.tenant_id != tenant.id:
            raise CashSessionError('La sesión no pertenece al tenant informado.')

        if session.estado != CashSession.States.ABIERTA:
            raise CashSessionError('Solo se pueden cerrar sesiones abiertas.')

        summary = get_session_summary(session)
        total_esperado = summary['total_esperado']

        breakdown = CashSessionSelector.get_session_payment_breakdown(session)

        # Agregar monto_apertura al breakdown del método Efectivo
        if session.monto_apertura > Decimal('0'):
            efectivo_pm = PaymentMethod.objects.for_tenant(tenant).filter(
                nombre__iexact='Efectivo', activo=True,
            ).first()
            if efectivo_pm:
                breakdown[efectivo_pm.pk] = breakdown.get(efectivo_pm.pk, Decimal('0')) + session.monto_apertura

        monto_cierre_declarado = Decimal('0')
        has_any_difference = False

        for detail in payment_details:
            pm_id = detail.get('payment_method_id')
            monto_declarado = Decimal(str(detail.get('monto_declarado', '0')))
            pm_comentario = detail.get('comentario', '')
            total_sistema = Decimal(str(breakdown.get(pm_id, '0')))
            diff = monto_declarado - total_sistema
            monto_cierre_declarado += monto_declarado

            if diff != Decimal('0'):
                has_any_difference = True
                if not pm_comentario.strip():
                    raise CashSessionError(
                        f'Debe explicar la diferencia en la cuadratura de cada medio de pago.'
                    )

            CashCloseDetail.objects.create(
                tenant=tenant,
                cash_session=session,
                payment_method_id=pm_id,
                monto_sistema=total_sistema,
                monto_declarado=monto_declarado,
                diferencia=diff,
                comentario=pm_comentario,
            )

        diferencia = monto_cierre_declarado - total_esperado

        session.estado = CashSession.States.CERRADA
        session.closed_by = user
        session.closed_at = timezone.now()
        session.monto_cierre_declarado = monto_cierre_declarado
        session.diferencia = diferencia
        session.comentario_cierre = comentario_cierre
        session.save(update_fields=[
            'estado', 'closed_by', 'closed_at',
            'monto_cierre_declarado', 'diferencia', 'comentario_cierre',
        ])

    return session


def register_cash_movement(*, user, tenant, session_id, tipo, monto, descripcion='', linked_transaction=None, payment_method_id=None):
    """Registra un movimiento manual de caja (ingreso, egreso o ajuste).

    Parámetros:
    - user: usuario que registra el movimiento.
    - tenant: tenant de la operación.
    - session_id: id de la sesión de caja.
    - tipo: tipo de movimiento (INGRESO, EGRESO, AJUSTE).
    - monto: monto del movimiento.
    - descripcion: descripción opcional para automáticos, obligatoria para manuales.
    - linked_transaction: transacción vinculada (opcional).
    - payment_method_id: id del medio de pago (obligatorio para AJUSTE, auto Efectivo para otros).

    Retorno:
    - CashMovement creado.
    """
    validate_tenant_access(user, tenant)

    monto = Decimal(monto)
    if monto <= Decimal('0'):
        raise CashMovementError('El monto del movimiento debe ser mayor que cero.')

    if tipo not in CashMovement.MovementType.values:
        raise CashMovementError(f'Tipo de movimiento inválido: {tipo}.')

    if linked_transaction is None and not descripcion.strip():
        raise CashMovementError('La descripción es obligatoria para movimientos manuales.')

    if tipo == CashMovement.MovementType.AJUSTE:
        if payment_method_id is None:
            raise CashMovementError('El medio de pago es obligatorio para movimientos de tipo AJUSTE.')
        payment_method = PaymentMethod.objects.for_tenant(tenant).get(pk=payment_method_id)
        if not payment_method.activo:
            raise CashMovementError('El método de pago seleccionado no está activo.')
    else:
        if payment_method_id:
            payment_method = PaymentMethod.objects.for_tenant(tenant).get(pk=payment_method_id)
        else:
            payment_method = PaymentMethod.objects.for_tenant(tenant).filter(
                nombre__iexact='Efectivo', activo=True,
            ).first()
            if payment_method is None:
                raise CashMovementError('No se encontró el método de pago Efectivo en este tenant.')

    with transaction.atomic():
        session = CashSession.objects.select_for_update().get(pk=session_id)

        if session.tenant_id != tenant.id:
            raise CashMovementError('La sesión no pertenece al tenant informado.')

        if session.estado != CashSession.States.ABIERTA:
            raise CashMovementError('Solo se pueden registrar movimientos en sesiones abiertas.')

        if linked_transaction is not None and linked_transaction.tenant_id != tenant.id:
            raise CashMovementError('La transacción no pertenece al tenant informado.')

        movement = CashMovement.objects.create(
            tenant=tenant,
            cash_session=session,
            transaction=linked_transaction,
            tipo=tipo,
            monto=monto,
            descripcion=descripcion,
            payment_method=payment_method,
        )

    return movement


def get_session_summary(session):
    """Calcula el resumen de cuadratura de una sesión de caja.

    Parámetros:
    - session: CashSession a resumir.

    Retorno:
    - dict con: monto_apertura, total_ingresos, total_egresos, total_ajustes, total_esperado, diferencia.
    """
    movements = CashMovement.objects.filter(cash_session=session)

    total_ingresos = movements.filter(tipo=CashMovement.MovementType.INGRESO).aggregate(
        total=Sum('monto')
    )['total'] or Decimal('0')

    total_egresos = movements.filter(tipo=CashMovement.MovementType.EGRESO).aggregate(
        total=Sum('monto')
    )['total'] or Decimal('0')

    total_ajustes = movements.filter(tipo=CashMovement.MovementType.AJUSTE).aggregate(
        total=Sum('monto')
    )['total'] or Decimal('0')

    total_esperado = session.monto_apertura + total_ingresos - total_egresos + total_ajustes

    diferencia = None
    if session.monto_cierre_declarado is not None:
        diferencia = session.monto_cierre_declarado - total_esperado

    return {
        'monto_apertura': session.monto_apertura,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'total_ajustes': total_ajustes,
        'total_esperado': total_esperado,
        'diferencia': diferencia,
    }