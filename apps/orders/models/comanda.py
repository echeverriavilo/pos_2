from django.db import models
from django.db.models import UniqueConstraint

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager
from apps.orders.models.dispositivo import Dispositivo
from apps.orders.models.order import Order
from apps.orders.models.order_item import OrderItem


class Comanda(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        LISTA = 'LISTA', 'Lista'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='comandas',
    )
    orden = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='comandas',
    )
    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.CASCADE,
        related_name='comandas',
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('-creado_en',)

    def __str__(self):
        return f"Comanda {self.id} - Orden {self.orden_id} - {self.dispositivo.nombre}"


class ComandaItem(models.Model):
    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name='items',
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.PROTECT,
        related_name='+',
    )
    cantidad = models.PositiveIntegerField(
        help_text="Cantidad snapshot del order item en el momento de asignación a la comanda"
    )
    precio_unitario_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Precio unitario snapshot del order item en el momento de asignación"
    )

    class Meta:
        unique_together = (('comanda', 'order_item'),)
        verbose_name = 'Ítem de Comanda'
        verbose_name_plural = 'Ítems de Comanda'

    def save(self, *args, **kwargs):
        if not self.pk:
            # Snapshot values on creation
            self.cantidad = self.order_item.cantidad
            self.precio_unitario_snapshot = self.order_item.precio_unitario_snapshot
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_item.product.nombre} x{self.cantidad} en Comanda {self.comanda_id}"