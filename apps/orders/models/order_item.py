from django.db import models

from apps.catalog.models import Product
from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager
from apps.orders.models.order import Order


class OrderItem(models.Model):
    class States(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PREPARACION = 'PREPARACION', 'Preparación'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        ANULADO = 'ANULADO', 'Anulado'
        PAGADO = 'PAGADO', 'Pagado'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='order_items',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=32, choices=States.choices, default=States.PENDIENTE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Item {self.pk} ({self.estado})"

    def save(self, *args, **kwargs):
        if self.order_id and self.order is None:
            self.order = Order.objects.filter(pk=self.order_id).first()
        if self.order is None or self.order.tenant is None:
            raise ValueError('OrderItem requiere una orden con tenant válido.')
        self.tenant = self.order.tenant
        if self.product.tenant != self.order.tenant:
            raise ValueError('El producto debe pertenecer al mismo tenant que la orden.')
        if self.pk:
            original = OrderItem.objects.filter(pk=self.pk).values('precio_unitario_snapshot').first()
            if original and original['precio_unitario_snapshot'] != self.precio_unitario_snapshot:
                raise ValueError('El precio unitario es inmutable una vez creado el ítem.')
        super().save(*args, **kwargs)
