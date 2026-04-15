from decimal import Decimal

from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager

from .category import Category


class Product(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='products',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
    )
    nombre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    precio_bruto = models.DecimalField(max_digits=12, decimal_places=2)
    es_inventariable = models.BooleanField(default=True)
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('nombre',)
        unique_together = (('tenant', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} ({self.tenant.slug})"
