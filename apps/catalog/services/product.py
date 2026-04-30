from decimal import Decimal

from django.core.exceptions import ValidationError

from apps.catalog.models import Product


class ProductService:
    @staticmethod
    def create_product(*, tenant, category, nombre: str, precio_bruto: Decimal, es_inventariable: bool = True, stock_actual: Decimal | None = None, description: str | None = None) -> Product:
        if not nombre:
            raise ValidationError('El nombre del producto es obligatorio.')
        if Product.objects.filter(tenant=tenant, nombre=nombre).exists():
            raise ValidationError(f'Ya existe un producto con el nombre "{nombre}".')
        if precio_bruto is None or precio_bruto < Decimal('0'):
            raise ValidationError('El precio bruto debe ser un valor no negativo.')
        stock = stock_actual if stock_actual is not None else Decimal('0')
        if stock < Decimal('0'):
            raise ValidationError('El stock inicial no puede ser negativo.')
        return Product.objects.create(
            tenant=tenant,
            category=category,
            nombre=nombre,
            precio_bruto=precio_bruto,
            es_inventariable=es_inventariable,
            stock_actual=stock,
            description=description or '',
        )

    @staticmethod
    def update_product(product: Product, *, nombre: str | None = None, precio_bruto: Decimal | None = None, es_inventariable: bool | None = None, category=None, description: str | None = None, stock_actual: Decimal | None = None) -> Product:
        updated_fields = []
        if nombre is not None:
            if not nombre:
                raise ValidationError('El nombre del producto no puede estar vacío.')
            if Product.objects.filter(tenant=product.tenant, nombre=nombre).exclude(pk=product.pk).exists():
                raise ValidationError(f'Ya existe un producto con el nombre "{nombre}".')
            product.nombre = nombre
            updated_fields.append('nombre')
        if precio_bruto is not None:
            if precio_bruto < Decimal('0'):
                raise ValidationError('El precio bruto debe ser no negativo.')
            product.precio_bruto = precio_bruto
            updated_fields.append('precio_bruto')
        if es_inventariable is not None:
            product.es_inventariable = es_inventariable
            updated_fields.append('es_inventariable')
        if category is not None:
            product.category = category
            updated_fields.append('category')
        if description is not None:
            product.description = description
            updated_fields.append('description')
        if stock_actual is not None:
            if stock_actual < Decimal('0'):
                raise ValidationError('El stock no puede ser negativo.')
            product.stock_actual = stock_actual
            updated_fields.append('stock_actual')
        if updated_fields:
            product.save(update_fields=updated_fields)
        return product

    @staticmethod
    def toggle_active(product: Product) -> Product:
        """Pausa o reanuda un producto (desactivación temporal)."""
        product.is_active = not product.is_active
        product.save(update_fields=['is_active'])
        return product
