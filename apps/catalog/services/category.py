from django.core.exceptions import ValidationError

from apps.catalog.models import Category


class CategoryService:
    @staticmethod
    def create_category(*, tenant, nombre: str) -> Category:
        if not nombre:
            raise ValidationError('El nombre de la categoría es obligatorio.')
        if Category.objects.filter(tenant=tenant, nombre=nombre).exists():
            raise ValidationError(f'Ya existe una categoría con el nombre "{nombre}".')
        return Category.objects.create(tenant=tenant, nombre=nombre)

    @staticmethod
    def update_category(category: Category, nombre: str) -> Category:
        if not nombre:
            raise ValidationError('El nombre de la categoría es obligatorio.')
        if Category.objects.filter(tenant=category.tenant, nombre=nombre).exclude(pk=category.pk).exists():
            raise ValidationError(f'Ya existe una categoría con el nombre "{nombre}".')
        category.nombre = nombre
        category.save(update_fields=['nombre'])
        return category

    @staticmethod
    def delete_category(category: Category) -> None:
        category.delete()

    @staticmethod
    def toggle_active(category: Category) -> Category:
        """Pausa o reanuda una categoría (desactivación temporal)."""
        category.is_active = not category.is_active
        category.save(update_fields=['is_active'])
        return category
