from decimal import Decimal
from typing import Iterable

from django.db import transaction

from apps.core.constants.actions import SystemActions
from apps.core.services.auth import validate_tenant_access, validate_role_permission
from apps.orders.models import CashMovement, Order, OrderItem, Transaction, TransactionItem
from apps.orders.selectors import TransactionSelector
from apps.orders.selectors.cash_session import CashSessionSelector
from apps.orders.services.order import OrderError, transition_order_state


class TransactionError(OrderError):
    pass


def _normalize_amount(amount) -> Decimal:
    """Normaliza y valida un monto ingresado manualmente.

    Parámetros:
    - amount: valor recibido para el pago.

    Retorno:
    - Decimal positivo.
    """

    if amount is None:
        raise TransactionError('El monto es obligatorio para este tipo de pago.')
    normalized_amount = Decimal(amount)
    if normalized_amount <= Decimal('0'):
        raise TransactionError('El monto debe ser mayor que cero.')
    return normalized_amount


def _validate_order_for_payment(order: Order, tenant) -> None:
    """Valida que una orden pueda recibir un nuevo pago.

    Parámetros:
    - order: orden objetivo.
    - tenant: tenant bajo el cual se ejecuta la operación.

    Retorno:
    - None.
    """

    if order.tenant_id != tenant.id:
        raise TransactionError('La orden debe pertenecer al tenant informado.')
    if order.estado in {Order.States.ANULADO, Order.States.COMPLETADO, Order.States.CONFIRMADO}:
        raise TransactionError('La orden no admite nuevos pagos en su estado actual.')


def _load_payment_items(*, tenant, order: Order, order_items: Iterable[OrderItem], cantidades: dict | None = None) -> list[OrderItem]:
    """Carga y bloquea los ítems seleccionados para pago por productos.

    Si se informa cantidades y alguna es menor a la cantidad del ítem,
    se crea un ítem residual con la diferencia y se reduce el original
    para marcarlo como PAGADO sin violar la invariante de inmutabilidad.

    Parámetros:
    - tenant: tenant de la operación.
    - order: orden pagada.
    - order_items: iterable de instancias o ids de OrderItem.
    - cantidades: dict opcional {item_id: cantidad_a_pagar}.

    Retorno:
    - Lista de OrderItem bloqueados para actualización.
    """

    item_ids = [item.pk if isinstance(item, OrderItem) else item for item in order_items]
    if not item_ids:
        raise TransactionError('El pago por productos requiere al menos un ítem.')

    locked_items = list(
        OrderItem.objects.for_tenant(tenant)
        .select_for_update()
        .filter(order=order, pk__in=item_ids)
        .select_related('product')
    )
    if len(locked_items) != len(set(item_ids)):
        raise TransactionError('Todos los ítems del pago deben pertenecer a la orden indicada.')

    for item in locked_items:
        if item.estado == OrderItem.States.ANULADO:
            raise TransactionError('No se pueden pagar ítems anulados.')
        if item.estado == OrderItem.States.PAGADO:
            raise TransactionError('No se pueden volver a pagar ítems ya pagados.')

    # Split items si se especifican cantidades parciales
    if cantidades:
        for item in locked_items:
            cant_a_pagar = cantidades.get(str(item.pk)) or cantidades.get(item.pk)
            if cant_a_pagar is not None:
                cant_a_pagar = int(cant_a_pagar)
                if cant_a_pagar <= 0:
                    raise TransactionError(f'La cantidad para "{item.product.nombre}" debe ser mayor que cero.')
                if cant_a_pagar > item.cantidad:
                    raise TransactionError(f'La cantidad para "{item.product.nombre}" no puede exceder {item.cantidad}.')
                if cant_a_pagar < item.cantidad:
                    # Crear ítem residual con la diferencia
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        cantidad=item.cantidad - cant_a_pagar,
                        precio_unitario_snapshot=item.precio_unitario_snapshot,
                        estado=item.estado,
                    )
                    item.cantidad = cant_a_pagar
                    item.save(update_fields=['cantidad'])

    return locked_items


def _calculate_items_amount(order_items: Iterable[OrderItem]) -> Decimal:
    """Suma el subtotal de los ítems seleccionados.

    Parámetros:
    - order_items: iterable de OrderItem válidos.

    Retorno:
    - Decimal con el monto calculado automáticamente.
    """

    total = Decimal('0')
    for item in order_items:
        total += item.precio_unitario_snapshot * item.cantidad
    return total


def apply_payment_to_items(*, transaction_record: Transaction, order_items: Iterable[OrderItem]) -> list[TransactionItem]:
    """Aplica un pago por productos marcando ítems y relaciones.

    Parámetros:
    - transaction_record: transacción de tipo PRODUCTOS ya creada.
    - order_items: iterable de OrderItem a marcar como pagados.

    Retorno:
    - Lista de TransactionItem creados.

    Efectos secundarios:
    - Cambia estado de los ítems a PAGADO y crea asociaciones TransactionItem.
    """

    if transaction_record.tipo_pago != Transaction.PaymentType.PRODUCTOS:
        raise TransactionError('Solo las transacciones PRODUCTOS pueden asociar ítems.')

    created_items = []
    with transaction.atomic():
        for order_item in order_items:
            order_item.estado = OrderItem.States.PAGADO
            order_item.save(update_fields=['estado'])
            created_items.append(
                TransactionItem.objects.create(
                    tenant=transaction_record.tenant,
                    transaction=transaction_record,
                    order_item=order_item,
                )
            )
    return created_items


def update_order_payment_state(*, user, order: Order) -> Order:
    """Actualiza el estado de una orden según el consumo pagado acumulado.

    El cierre de mesa se determina por consumo pagado >= total_bruto.
    La propina es voluntaria y no afecta las transiciones de estado.

    Parámetros:
    - user: usuario que ejecuta la operación
    - order: orden cuyo estado de pago debe reevaluarse.

    Retorno:
    - Order actualizada.

    Efectos secundarios:
    - Puede cambiar estado de la orden, liberar mesa y disparar inventario.
    """

    with transaction.atomic():
        locked_order = Order.objects.select_for_update().get(pk=order.pk)
        total_consumo_paid = TransactionSelector.total_consumo_paid(locked_order)
        total_consumo = TransactionSelector.total_cuenta(locked_order)
        if total_consumo_paid > total_consumo:
            raise TransactionError('El consumo pagado no puede exceder el total de consumo.')

        if total_consumo_paid == Decimal('0'):
            return locked_order

        if locked_order.tipo_flujo == Order.Flow.MESA:
            if total_consumo_paid < total_consumo:
                if locked_order.estado == Order.States.ABIERTO:
                    transition_order_state(user=user, order=locked_order, target_state=Order.States.PAGADO_PARCIAL)
                return locked_order

            if locked_order.estado in {Order.States.ABIERTO, Order.States.PAGADO_PARCIAL}:
                transition_order_state(
                    user=user,
                    order=locked_order,
                    target_state=Order.States.COMPLETADO,
                    total_pagado=total_consumo_paid,
                )
            return locked_order

        if total_consumo_paid < total_consumo:
            if locked_order.estado == Order.States.ABIERTO:
                transition_order_state(user=user, order=locked_order, target_state=Order.States.PAGADO_PARCIAL)
            return locked_order

        if locked_order.estado == Order.States.ABIERTO:
            transition_order_state(user=user, order=locked_order, target_state=Order.States.PAGADO_PARCIAL)
        if locked_order.estado == Order.States.PAGADO_PARCIAL:
            transition_order_state(
                user=user,
                order=locked_order,
                target_state=Order.States.CONFIRMADO,
                total_pagado=total_consumo_paid,
            )
        return locked_order


def register_transaction(*, user, tenant, order: Order, payment_type: str, amount=None, order_items=None, cantidades=None, payment_method=None, tip_amount=None) -> Transaction:
    """Registra una transacción de pago respetando invariantes del dominio.

    Requiere una CashSession abierta compatible con el flujo de la orden.
    Crea un CashMovement tipo INGRESO vinculado a la sesión.

    Parámetros:
    - user: usuario que registra el pago.
    - tenant: tenant de la operación.
    - order: orden a pagar.
    - payment_type: tipo de pago TOTAL, ABONO o PRODUCTOS.
    - amount: monto opcional según tipo.
    - order_items: ítems opcionales para pagos por productos.
    - cantidades: dict opcional {item_id: cantidad_a_pagar} para pago parcial por cantidad.
    - payment_method: instancia de PaymentMethod para esta transacción.
    - tip_amount: monto de propina para esta transacción (opcional, sin límite superior).

    Retorno:
    - Transaction creada.

    Efectos secundarios:
    - Puede marcar ítems como pagados, cambiar el estado de la orden y crear CashMovement.
    """
    validate_tenant_access(user, tenant)
    validate_role_permission(user, SystemActions.REGISTER_PAYMENT)

    with transaction.atomic():
        locked_order = Order.objects.for_tenant(tenant).select_for_update().get(pk=order.pk)
        _validate_order_for_payment(locked_order, tenant)

        cash_session = CashSessionSelector.get_active_session_for_order(tenant, locked_order)
        if cash_session is None:
            raise TransactionError('No hay una sesión de caja abierta compatible con esta orden.')

        pending_consumo = TransactionSelector.total_pending(locked_order)
        if pending_consumo <= Decimal('0'):
            raise TransactionError('La orden no tiene saldo pendiente.')

        if payment_method is None:
            raise TransactionError('El método de pago es obligatorio.')
        if not payment_method.activo:
            raise TransactionError('El método de pago seleccionado no está activo.')
        if payment_method.tenant_id != tenant.id:
            raise TransactionError('El método de pago debe pertenecer al tenant de la operación.')

        tip_amount = Decimal(tip_amount) if tip_amount is not None else Decimal('0')
        if tip_amount < Decimal('0'):
            raise TransactionError('El monto de propina no puede ser negativo.')

        locked_items = []
        if payment_type == Transaction.PaymentType.TOTAL:
            transaction_amount = pending_consumo
            if amount is not None and Decimal(amount) != pending_consumo:
                raise TransactionError('El pago TOTAL debe coincidir exactamente con el saldo pendiente.')
            if order_items:
                raise TransactionError('El pago TOTAL no admite selección de ítems.')
        elif payment_type == Transaction.PaymentType.ABONO:
            transaction_amount = _normalize_amount(amount)
            if order_items:
                raise TransactionError('El ABONO no admite selección de ítems.')
        elif payment_type == Transaction.PaymentType.PRODUCTOS:
            if locked_order.tipo_flujo != Order.Flow.MESA:
                raise TransactionError('El pago por PRODUCTOS solo aplica al flujo MESA.')
            if TransactionSelector.list_for_order(locked_order).filter(tipo_pago=Transaction.PaymentType.ABONO).exists():
                raise TransactionError('No se puede usar PRODUCTOS después de registrar un ABONO.')
            locked_items = _load_payment_items(
                tenant=tenant,
                order=locked_order,
                order_items=order_items or [],
                cantidades=cantidades,
            )
            transaction_amount = _calculate_items_amount(locked_items)
            if amount is not None and Decimal(amount) != transaction_amount:
                raise TransactionError('El monto de PRODUCTOS se calcula automáticamente.')
        else:
            raise TransactionError('Tipo de pago no soportado.')

        if transaction_amount > pending_consumo:
            raise TransactionError('El monto del pago no puede exceder el consumo pendiente.')

        transaction_record = Transaction.objects.create(
            tenant=tenant,
            order=locked_order,
            monto=transaction_amount,
            tipo_pago=payment_type,
            payment_method=payment_method,
            tip_amount=tip_amount,
        )

        if payment_type == Transaction.PaymentType.PRODUCTOS:
            apply_payment_to_items(transaction_record=transaction_record, order_items=locked_items)

        CashMovement.objects.create(
            tenant=tenant,
            cash_session=cash_session,
            transaction=transaction_record,
            payment_method=payment_method,
            tipo=CashMovement.MovementType.INGRESO,
            monto=transaction_amount + tip_amount,
            descripcion=f'Pago {payment_type} orden #{locked_order.pk}',
        )

        update_order_payment_state(user=user, order=locked_order)
        return transaction_record
