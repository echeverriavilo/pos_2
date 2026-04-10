from decimal import Decimal

from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager

from .product import Product


class StockMovement(models.Model):
    class Types(models.TextChoices):
        INGRESO = 'INGRESO', 'Ingreso'
        AJUSTE = 'AJUSTE', 'Ajuste'
        VENTA = 'VENTA', 'Venta'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='stock_movements',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
    )
    tipo = models.CharField(max_length=20, choices=Types.choices)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"[{self.tipo}] {self.product.nombre}: {self.cantidad}"
