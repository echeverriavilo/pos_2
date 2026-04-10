from apps.catalog.models import Ingredient


class IngredientSelector:
    @staticmethod
    def list_for_tenant(tenant):
        return Ingredient.objects.for_tenant(tenant)

    @staticmethod
    def get_by_id(pk):
        return Ingredient.objects.filter(pk=pk).first()
