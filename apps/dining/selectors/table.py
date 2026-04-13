from apps.dining.models import DiningTable
from apps.orders.models import Order


class DiningTableSelector:
    @staticmethod
    def list_for_tenant(tenant):
        return DiningTable.objects.for_tenant(tenant)

    @staticmethod
    def get_for_tenant(tenant, pk):
        return DiningTable.objects.for_tenant(tenant).filter(pk=pk).first()

    @staticmethod
    def get_active_order_for_table(table):
        if table is None or table.tenant is None:
            return None
        return Order.objects.for_tenant(table.tenant).filter(
            table=table,
            estado__in=Order.ACTIVE_STATES,
        ).first()
