from apps.catalog.models import Category


class CategorySelector:
    @staticmethod
    def list_for_tenant(tenant):
        return Category.objects.for_tenant(tenant)

    @staticmethod
    def get_by_id(pk):
        return Category.objects.filter(pk=pk).first()
