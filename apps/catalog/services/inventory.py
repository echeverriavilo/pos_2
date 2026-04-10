from decimal import Decimal

from django.db import transaction

from apps.catalog.models import Product, StockMovement


class InventoryError(Exception):
    pass


class InventoryService:
    @classmethod
    def registrar_ingreso(cls, *, product: Product, cantidad: Decimal) -> StockMovement:
        if cantidad <= Decimal('0'):
            raise InventoryError('La cantidad de ingreso debe ser mayor que cero.')
        return cls._registrar_movimiento(product, StockMovement.Types.INGRESO, cantidad)

    @classmethod
    def registrar_ajuste(cls, *, product: Product, cantidad: Decimal) -> StockMovement:
        if cantidad == Decimal('0'):
            raise InventoryError('El ajuste debe tener una cantidad distinta de cero.')
        return cls._registrar_movimiento(product, StockMovement.Types.AJUSTE, cantidad)

    @classmethod
    def registrar_venta(cls, *, product: Product, cantidad: Decimal) -> StockMovement:
        if cantidad <= Decimal('0'):
            raise InventoryError('La cantidad de venta debe ser mayor que cero.')
        return cls._registrar_movimiento(product, StockMovement.Types.VENTA, -abs(cantidad))

    @classmethod
    def _registrar_movimiento(cls, product: Product, tipo: str, cantidad: Decimal) -> StockMovement:
        with transaction.atomic():
            nuevo_stock = product.stock_actual + cantidad
            if product.es_inventariable and nuevo_stock < Decimal('0'):
                raise InventoryError('No se puede llevar el stock por debajo de cero.')
            product.stock_actual = nuevo_stock
            product.save(update_fields=['stock_actual'])
            return StockMovement.objects.create(
                tenant=product.tenant,
                product=product,
                tipo=tipo,
                cantidad=cantidad,
            )
