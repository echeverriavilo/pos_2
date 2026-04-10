from apps.catalog.models import Product


class ProductSelector:
    @staticmethod
    def list_for_tenant(tenant):
        return Product.objects.for_tenant(tenant).select_related('category')

    @staticmethod
    def get_for_tenant(tenant, pk):
        return Product.objects.for_tenant(tenant).filter(pk=pk).select_related('category').first()

    @staticmethod
    def get_stock(product: Product):
        return product.stock_actual
