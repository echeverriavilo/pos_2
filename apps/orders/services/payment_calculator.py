from decimal import Decimal

from django.db import transaction

from apps.core.constants.actions import SystemActions
from apps.core.services.auth import validate_tenant_access, validate_role_permission
from apps.orders.models import Order
from apps.orders.services.order import OrderError


class PaymentCalculatorError(OrderError):
    pass


def calculate_iva_breakdown(order: Order, tenant) -> dict:
    """Calcula el desglose de IVA según la configuración del tenant.

    Parámetros:
    - order: orden de la cual se calcula el desglose.
    - tenant: tenant cuya configuración de IVA se utiliza.

    Retorno:
    - Diccionario con claves 'neto', 'iva' y 'total_bruto', todos Decimal.
    """
    config_iva = tenant.config_iva
    total_bruto = order.total_bruto
    neto = (total_bruto / (Decimal('1') + config_iva)).quantize(Decimal('0.01'))
    iva = total_bruto - neto
    return {
        'neto': neto,
        'iva': iva,
        'total_bruto': total_bruto,
    }


def calculate_suggested_tip(order: Order) -> Decimal:
    """Calcula la propina sugerida como 10% del total bruto.

    Parámetros:
    - order: orden para la cual se sugiere la propina.

    Retorno:
    - Decimal con el monto sugerido de propina.
    """
    return order.total_bruto * Decimal('0.10')


def set_tip(user, order: Order, amount: Decimal) -> Order:
    """Establece el monto de propina en una orden.

    Parámetros:
    - user: usuario que ejecuta la operación.
    - order: orden a modificar.
    - amount: monto de propina a establecer.

    Retorno:
    - Order actualizada con la nueva propina.

    Efectos secundarios:
    - Actualiza order.propina_monto dentro de una transacción atómica.
    """
    validate_role_permission(user, SystemActions.REGISTER_PAYMENT)
    validate_tenant_access(user, order.tenant)

    active_states = {Order.States.ABIERTO, Order.States.PAGADO_PARCIAL}
    if order.estado not in active_states:
        raise PaymentCalculatorError('Solo se puede modificar la propina en órdenes abiertas o con pago parcial.')

    amount = Decimal(amount)
    if amount < Decimal('0'):
        raise PaymentCalculatorError('El monto de propina no puede ser negativo.')

    with transaction.atomic():
        locked_order = Order.objects.select_for_update().get(pk=order.pk)
        locked_order.propina_monto = amount
        locked_order.save(update_fields=['propina_monto'])
        return locked_order
