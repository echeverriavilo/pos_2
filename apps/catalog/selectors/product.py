from django.db.models import Q

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

    @staticmethod
    def search_active_products(tenant, category_id=None, search_term=None):
        """
        Busca productos activos del tenant, filtrando opcionalmente por categoría y término de búsqueda.
        
        Args:
            tenant: Tenant del cual obtener productos
            category_id: ID de categoría (opcional)
            search_term: Término de búsqueda en nombre o descripción (opcional)
        
        Returns:
            QuerySet de productos filtrados y ordenados por nombre
        """
        queryset = Product.objects.for_tenant(tenant).filter(is_active=True)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search_term:
            queryset = queryset.filter(
                Q(nombre__icontains=search_term) |
                Q(description__icontains=search_term)
            )

        return queryset.select_related('category').order_by('nombre')
