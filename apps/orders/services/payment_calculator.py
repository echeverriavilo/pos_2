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



