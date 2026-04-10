from apps.catalog.models import StockMovement


class StockMovementSelector:
    @staticmethod
    def list_for_product(product):
        return StockMovement.objects.for_tenant(product.tenant).filter(product=product)

    @staticmethod
    def list_for_tenant(tenant):
        return StockMovement.objects.for_tenant(tenant)
