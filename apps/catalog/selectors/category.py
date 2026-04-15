from apps.catalog.models import Category


class CategorySelector:
    @staticmethod
    def list_for_tenant(tenant):
        return Category.objects.for_tenant(tenant)

    @staticmethod
    def get_by_id(tenant, pk):
        """Obtiene una categoría por ID validando que pertenezca al tenant."""
        return Category.objects.for_tenant(tenant).filter(pk=pk).first()

    @staticmethod
    def get_active_categories(tenant):
        return Category.objects.for_tenant(tenant).filter(is_active=True).order_by('nombre')
