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
    def total_pending(order):
        """Calcula el monto pendiente de una orden.

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente a total_bruto menos total pagado.
        """

        return order.total_bruto - TransactionSelector.total_paid(order)
