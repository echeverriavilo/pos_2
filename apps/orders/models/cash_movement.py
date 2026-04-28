from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager
from apps.orders.models.cash_session import CashSession
from apps.orders.models.payment_method import PaymentMethod
from apps.orders.models.transaction import Transaction


class CashMovement(models.Model):
    class MovementType(models.TextChoices):
        INGRESO = 'INGRESO', 'Ingreso'
        EGRESO = 'EGRESO', 'Egreso'
        AJUSTE = 'AJUSTE', 'Ajuste'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='cash_movements',
    )
    cash_session = models.ForeignKey(
        CashSession,
        on_delete=models.PROTECT,
        related_name='movements',
    )
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        related_name='cash_movements',
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='cash_movements',
        null=True,
        blank=True,
    )
    tipo = models.CharField(
        max_length=16,
        choices=MovementType.choices,
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"CashMovement {self.pk} ({self.tipo}) ${self.monto}"