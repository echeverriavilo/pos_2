from decimal import Decimal

from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager
from apps.orders.models.cash_session import CashSession
from apps.orders.models.payment_method import PaymentMethod


class CashCloseDetail(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='cash_close_details',
    )
    cash_session = models.ForeignKey(
        CashSession,
        on_delete=models.CASCADE,
        related_name='close_details',
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='cash_close_details',
    )
    monto_sistema = models.DecimalField(max_digits=12, decimal_places=2)
    monto_declarado = models.DecimalField(max_digits=12, decimal_places=2)
    diferencia = models.DecimalField(max_digits=12, decimal_places=2)
    comentario = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('cash_session', 'payment_method')

    def __str__(self):
        return f"CashCloseDetail {self.pk} ({self.payment_method.nombre})"
