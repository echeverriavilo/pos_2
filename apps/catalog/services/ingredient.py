from django.core.exceptions import ValidationError

from apps.catalog.models import Ingredient


class IngredientService:
    @staticmethod
    def create_ingredient(*, tenant, nombre: str) -> Ingredient:
        if not nombre:
            raise ValidationError('El nombre del ingrediente es obligatorio.')
        return Ingredient.objects.create(tenant=tenant, nombre=nombre)

    @staticmethod
    def update_ingredient(ingredient: Ingredient, *, nombre: str) -> Ingredient:
        if not nombre:
            raise ValidationError('El nombre del ingrediente es obligatorio.')
        ingredient.nombre = nombre
        ingredient.save(update_fields=['nombre'])
        return ingredient

    @staticmethod
    def delete_ingredient(ingredient: Ingredient) -> None:
        ingredient.delete()
