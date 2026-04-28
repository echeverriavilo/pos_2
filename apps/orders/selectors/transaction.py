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
    def total_cuenta(order):
        """Calcula el total de consumo de una orden (sin propina).

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente a total_bruto.
        """

        return order.total_bruto

    @staticmethod
    def total_consumo_paid(order):
        """Calcula el total de consumo pagado (excluyendo propinas).

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal con la suma de montos de transacciones (sin tip_amount).
        """

        aggregate = TransactionSelector.list_for_order(order).aggregate(total=Sum('monto'))
        return aggregate['total'] or Decimal('0')

    @staticmethod
    def total_tip_paid(order):
        """Calcula el total de propinas pagadas mediante transacciones.

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente a la suma de tip_amount de las transacciones.
        """

        aggregate = TransactionSelector.list_for_order(order).aggregate(total=Sum('tip_amount'))
        return aggregate['total'] or Decimal('0')

    @staticmethod
    def total_pending(order):
        """Calcula el consumo pendiente de una orden (sin incluir propina).

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente a total_bruto menos consumo pagado.
        """

        return TransactionSelector.total_cuenta(order) - TransactionSelector.total_consumo_paid(order)

    @staticmethod
    def suggested_tip(order):
        """Calcula la propina sugerida del 10% sobre el total de consumo.

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente al 10% del total_bruto.
        """

        return order.total_bruto * Decimal('0.10')

    @staticmethod
    def suggested_tip_pending(order):
        """Calcula la propina sugerida sobre el consumo pendiente.

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente al 10% del consumo pendiente, sin bajar de cero.
        """

        pending = TransactionSelector.total_pending(order)
        return pending * Decimal('0.10')

    @staticmethod
    def total_pending_with_tip(order):
        """Calcula el total pendiente incluyendo propina sugerida (informativo).

        Parámetros:
        - order: orden objetivo.

        Retorno:
        - Decimal correspondiente a consumo pendiente + propina sugerida sobre pendiente.
        """

        return TransactionSelector.total_pending(order) + TransactionSelector.suggested_tip_pending(order)

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
