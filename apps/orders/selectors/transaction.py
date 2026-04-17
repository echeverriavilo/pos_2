from decimal import Decimal

from django.db.models import Sum

from apps.orders.models import Transaction


class TransactionSelector:
    @staticmethod
    def list_for_order(order):
        """Devuelve las transacciones registradas para una orden.

        Parámetros:
        - order: orden sobre la cual se consultan transacciones.

        Retorno:
        - QuerySet de Transaction filtrado por tenant y orden.
        """

        return Transaction.objects.for_tenant(order.tenant).filter(order=order)

    @staticmethod
    def total_paid(order):
        """Calcula el total pagado acumulado de una orden.

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal con la suma de montos registrados.
        """

        aggregate = TransactionSelector.list_for_order(order).aggregate(total=Sum('monto'))
        return aggregate['total'] or Decimal('0')

    @staticmethod
    def total_cuenta(order):
        """Calcula el total de la cuenta incluyendo propina.

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente a total_bruto más propina_monto.
        """

        return order.total_bruto + order.propina_monto

    @staticmethod
    def total_pending(order):
        """Calcula el monto pendiente de una orden.

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente a total_cuenta menos total pagado.
        """

        return TransactionSelector.total_cuenta(order) - TransactionSelector.total_paid(order)

    @staticmethod
    def items_paid_amount(order):
        """Calcula el monto total pagado mediante transacciones de tipo PRODUCTOS.

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal con la suma de montos de transacciones tipo PRODUCTOS.
        """

        aggregate = TransactionSelector.list_for_order(order).filter(
            tipo_pago=Transaction.PaymentType.PRODUCTOS
        ).aggregate(total=Sum('monto'))
        return aggregate['total'] or Decimal('0')
