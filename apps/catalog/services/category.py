from django.core.exceptions import ValidationError

from apps.catalog.models import Category


class CategoryService:
    @staticmethod
    def create_category(*, tenant, nombre: str) -> Category:
        if not nombre:
            raise ValidationError('El nombre de la categoría es obligatorio.')
        return Category.objects.create(tenant=tenant, nombre=nombre)

    @staticmethod
    def update_category(category: Category, nombre: str) -> Category:
        if not nombre:
            raise ValidationError('El nombre de la categoría es obligatorio.')
        category.nombre = nombre
        category.save(update_fields=['nombre'])
        return category

    @staticmethod
    def delete_category(category: Category) -> None:
        category.delete()
