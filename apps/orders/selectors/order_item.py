from apps.orders.models import OrderItem


class OrderItemSelector:
    @staticmethod
    def list_for_order(order):
        """Devuelve los ítems registrados en una orden específica."""
        return OrderItem.objects.for_tenant(order.tenant).filter(order=order)
