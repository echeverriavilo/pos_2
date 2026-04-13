from apps.dining.models import DiningTable
from apps.orders.selectors import OrderSelector


class DiningTableSelector:
    @staticmethod
    def list_for_tenant(tenant):
        return DiningTable.objects.for_tenant(tenant)

    @staticmethod
    def get_for_tenant(tenant, pk):
        return DiningTable.objects.for_tenant(tenant).filter(pk=pk).first()

    @staticmethod
    def get_active_order_for_table(table):
        return OrderSelector.get_active_order_for_table(table)
