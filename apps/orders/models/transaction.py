from decimal import Decimal

from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager
from apps.orders.models.order import Order
from apps.orders.models.order_item import OrderItem


class Transaction(models.Model):
    class PaymentType(models.TextChoices):
        TOTAL = 'TOTAL', 'Total'
        ABONO = 'ABONO', 'Abono'
        PRODUCTOS = 'PRODUCTOS', 'Productos'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_pago = models.CharField(max_length=16, choices=PaymentType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('-created_at', '-id')

    def __str__(self):
        return f"Transaction {self.pk} ({self.tipo_pago})"

    def save(self, *args, **kwargs):
        if self.order_id and self.__dict__.get('order') is None:
            self.order = Order.objects.select_related('tenant').filter(pk=self.order_id).first()
        if self.order is None or self.order.tenant is None:
            raise ValueError('La transacción requiere una orden con tenant válido.')
        if self.tenant_id and self.tenant_id != self.order.tenant_id:
            raise ValueError('La transacción debe pertenecer al mismo tenant que la orden.')
        if Decimal(self.monto) <= Decimal('0'):
            raise ValueError('El monto de la transacción debe ser mayor que cero.')
        self.tenant = self.order.tenant
        super().save(*args, **kwargs)


class TransactionItem(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='transaction_items',
    )
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='items',
    )
    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.PROTECT,
        related_name='transaction_items',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('created_at', 'id')
        unique_together = (
            ('transaction', 'order_item'),
            ('tenant', 'order_item'),
        )

    def __str__(self):
        return f"TransactionItem {self.pk}"

    def save(self, *args, **kwargs):
        if self.transaction_id and self.__dict__.get('transaction') is None:
            self.transaction = Transaction.objects.select_related('tenant').filter(pk=self.transaction_id).first()
        if self.order_item_id and self.__dict__.get('order_item') is None:
            self.order_item = OrderItem.objects.select_related('tenant').filter(pk=self.order_item_id).first()
        if self.transaction is None or self.order_item is None:
            raise ValueError('TransactionItem requiere transacción e ítem válidos.')
        if self.transaction.tenant_id != self.order_item.tenant_id:
            raise ValueError('La transacción y el ítem deben pertenecer al mismo tenant.')
        if self.transaction.order_id != self.order_item.order_id:
            raise ValueError('La transacción y el ítem deben pertenecer a la misma orden.')
        self.tenant = self.transaction.tenant
        super().save(*args, **kwargs)
