from decimal import Decimal

from django.db import transaction

from apps.orders.models import Order


class OrderCreationError(Exception):
    pass


def create_order_for_table(*, table):
    if table is None:
        raise OrderCreationError('Se requiere una mesa para crear un pedido.')
    if table.estado != table.States.DISPONIBLE:
        raise OrderCreationError('La mesa debe estar DISPONIBLE para abrir un pedido.')

    existing = Order.objects.for_tenant(table.tenant).filter(
        table=table,
        estado__in=Order.ACTIVE_STATES,
    )
    if existing.exists():
        raise OrderCreationError('Ya existe un pedido activo para esta mesa.')

    with transaction.atomic():
        return Order.objects.create(
            tenant=table.tenant,
            tipo_flujo=Order.Flow.MESA,
            table=table,
            estado=Order.States.ABIERTO,
            total_bruto=Decimal('0'),
            propina_monto=Decimal('0'),
        )
