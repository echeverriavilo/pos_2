from apps.orders.models import OrderItem


class OrderItemSelector:
    @staticmethod
    def list_for_order(order):
        """Devuelve los ítems registrados en una orden específica."""
        return OrderItem.objects.for_tenant(order.tenant).filter(order=order)

    @staticmethod
    def get_unpaid_items(order):
        """Devuelve los ítems no pagados de una orden.

        Parámetros:
        - order: orden sobre la cual se consultan los ítems.

        Retorno:
        - QuerySet de OrderItem con estado diferente a PAGADO y ANULADO,
          con select_related('product').
        """
        return OrderItem.objects.for_tenant(order.tenant).filter(
            order=order,
        ).exclude(
            estado__in=[OrderItem.States.PAGADO, OrderItem.States.ANULADO]
        ).select_related('product')

    @staticmethod
    def get_paid_items(order):
        """Devuelve los ítems pagados de una orden.

        Parámetros:
        - order: orden sobre la cual se consultan los ítems.

        Retorno:
        - QuerySet de OrderItem con estado PAGADO,
          con select_related('product').
        """
        return OrderItem.objects.for_tenant(order.tenant).filter(
            order=order,
            estado=OrderItem.States.PAGADO,
        ).select_related('product')
