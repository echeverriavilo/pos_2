from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.db.models import DecimalField, F, Sum

from apps.catalog.models import Product
from apps.catalog.services.inventory import InventoryService
from apps.dining.models import DiningTable
from apps.orders.models import Order, OrderItem


class OrderError(Exception):
    pass


class OrderItemError(OrderError):
    pass


class OrderStateTransitionError(OrderError):
    pass


FLOW_TRANSITIONS = {
    Order.Flow.MESA: {
        Order.States.ABIERTO: {Order.States.PAGADO_PARCIAL, Order.States.COMPLETADO, Order.States.ANULADO},
        Order.States.PAGADO_PARCIAL: {Order.States.COMPLETADO, Order.States.ANULADO},
    },
    Order.Flow.RAPIDO: {
        Order.States.ABIERTO: {Order.States.PAGADO_PARCIAL, Order.States.ANULADO},
        Order.States.PAGADO_PARCIAL: {Order.States.CONFIRMADO, Order.States.ANULADO},
        Order.States.CONFIRMADO: {Order.States.COMPLETADO, Order.States.ANULADO},
    },
}

REQUIRES_PAYMENT = {
    (Order.Flow.MESA, Order.States.ABIERTO, Order.States.COMPLETADO),
    (Order.Flow.MESA, Order.States.PAGADO_PARCIAL, Order.States.COMPLETADO),
    (Order.Flow.RAPIDO, Order.States.PAGADO_PARCIAL, Order.States.CONFIRMADO),
}


def _apply_rapid_inventory_discount(order: Order) -> None:
    """Descuenta stock al confirmar una orden de flujo rápido.

    Parámetros:
    - order: orden rápida ya validada para confirmación.

    Retorno:
    - None.

    Efectos secundarios:
    - Crea movimientos de inventario por cada ítem activo inventariable.
    """

    for item in order.items.exclude(estado=OrderItem.States.ANULADO).select_related('product'):
        if not item.product.es_inventariable:
            continue
        InventoryService.registrar_venta(product=item.product, cantidad=Decimal(item.cantidad))


def _validate_flow_constraints(tipo_flujo, table):
    if tipo_flujo == Order.Flow.MESA and table is None:
        raise OrderError('El flujo de mesa requiere una mesa asociada.')
    if tipo_flujo == Order.Flow.RAPIDO and table is not None:
        raise OrderError('El flujo rápido no puede estar vinculado a una mesa.')


def _ensure_overdraft_payment(order, total_pagado):
    if total_pagado is None:
        raise OrderStateTransitionError('Se requiere el monto pagado para esta transición.')
    total_pagado = Decimal(total_pagado)
    if total_pagado < order.total_bruto:
        raise OrderStateTransitionError('El pago total no alcanza el total bruto de la orden.')


def create_order(*, tenant, tipo_flujo, table=None, propina_monto=Decimal('0')) -> Order:
    """Crea una orden válida según el flujo definido y asigna valores iniciales."""
    _validate_flow_constraints(tipo_flujo, table)
    with transaction.atomic():
        return Order.objects.create(
            tenant=tenant,
            tipo_flujo=tipo_flujo,
            table=table,
            estado=Order.States.ABIERTO,
            total_bruto=Decimal('0'),
            propina_monto=propina_monto,
        )


def create_order_for_table(*, table) -> Order:
    """Conveniencia para crear órdenes del flujo MESA desde DiningTableService."""
    if table is None or table.tenant is None:
        raise OrderError('La mesa debe existir y pertenecer a un tenant.')
    return create_order(tenant=table.tenant, tipo_flujo=Order.Flow.MESA, table=table)


def add_item(*, order, product: Product, cantidad: int) -> OrderItem:
    """Agrega un ítem a la orden, ajusta el total y define el estado inicial."""
    if order.estado in {Order.States.COMPLETADO, Order.States.ANULADO}:
        raise OrderItemError('No se puede modificar una orden cerrada.')
    if product.tenant != order.tenant:
        raise OrderItemError('Producto y orden deben pertenecer al mismo tenant.')
    if cantidad <= 0:
        raise OrderItemError('La cantidad debe ser mayor que cero.')
    estado_inicial = (
        OrderItem.States.PREPARACION if order.tipo_flujo == Order.Flow.MESA else OrderItem.States.PENDIENTE
    )
    with transaction.atomic():
        item = OrderItem.objects.create(
            order=order,
            product=product,
            cantidad=cantidad,
            precio_unitario_snapshot=product.precio_bruto,
            estado=estado_inicial,
        )
        recalculate_total(order)
        return item


def remove_item(*, item: OrderItem) -> OrderItem:
    """Anula un ítem siempre que no haya sido pagado o ya anulado."""
    if item.estado == OrderItem.States.PAGADO:
        raise OrderItemError('No se pueden anular ítems pagados.')
    if item.estado == OrderItem.States.ANULADO:
        raise OrderItemError('El ítem ya se encuentra anulado.')
    with transaction.atomic():
        item.estado = OrderItem.States.ANULADO
        item.save(update_fields=['estado'])
        recalculate_total(item.order)
        return item


def recalculate_total(order: Order) -> Decimal:
    """Recalcula el total bruto considerando los ítems activos."""
    aggregate = order.items.exclude(estado=OrderItem.States.ANULADO).aggregate(
        total=Sum(
            F('precio_unitario_snapshot') * F('cantidad'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )
    total = aggregate['total'] or Decimal('0')
    order.total_bruto = total
    order.save(update_fields=['total_bruto'])
    return total


def transition_order_state(*, order: Order, target_state: str, total_pagado: Optional[Decimal] = None) -> Order:
    """Actualiza el estado de la orden validando las transiciones permitidas por flujo."""
    if order.estado == target_state:
        raise OrderStateTransitionError('La orden ya se encuentra en el estado solicitado.')
    valid_targets = FLOW_TRANSITIONS.get(order.tipo_flujo, {}).get(order.estado, set())
    if target_state not in valid_targets:
        raise OrderStateTransitionError('Transición inválida para el flujo actual.')
    if (order.tipo_flujo, order.estado, target_state) in REQUIRES_PAYMENT:
        _ensure_overdraft_payment(order, total_pagado)
    with transaction.atomic():
        order.estado = target_state
        order.save(update_fields=['estado'])
        if order.tipo_flujo == Order.Flow.RAPIDO and target_state == Order.States.CONFIRMADO:
            _apply_rapid_inventory_discount(order)
            order.items.filter(estado=OrderItem.States.PENDIENTE).update(estado=OrderItem.States.PREPARACION)
        if target_state == Order.States.COMPLETADO:
            order.items.filter(
                estado__in=(OrderItem.States.PENDIENTE, OrderItem.States.PREPARACION)
            ).update(estado=OrderItem.States.ENTREGADO)
            if order.table_id:
                order.table.estado = DiningTable.States.DISPONIBLE
                order.table.save(update_fields=['estado'])
        return order
