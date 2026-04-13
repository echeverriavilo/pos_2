from apps.orders.models import Order


class OrderSelector:
    @staticmethod
    def list_for_tenant(tenant):
        """Devuelve todas las órdenes asociadas al tenant."""
        return Order.objects.for_tenant(tenant)

    @staticmethod
    def get_active_order_for_table(table):
        """Busca la orden activa vinculada a una mesa específica."""
        if table is None or table.tenant is None:
            return None
        return Order.objects.for_tenant(table.tenant).filter(
            table=table,
            estado__in=Order.ACTIVE_STATES,
        ).first()
