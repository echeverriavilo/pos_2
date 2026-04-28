from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager
from apps.orders.models.cash_register import CashRegister


class CashSession(models.Model):
    class States(models.TextChoices):
        ABIERTA = 'ABIERTA', 'Abierta'
        CERRADA = 'CERRADA', 'Cerrada'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='cash_sessions',
    )
    cash_register = models.ForeignKey(
        CashRegister,
        on_delete=models.PROTECT,
        related_name='sessions',
    )
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sessions_opened',
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sessions_closed',
        null=True,
        blank=True,
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=16,
        choices=States.choices,
        default=States.ABIERTA,
    )
    monto_apertura = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
    )
    monto_cierre_declarado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    diferencia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    comentario_cierre = models.TextField(blank=True, default='')

    objects = TenantAwareManager()

    class Meta:
        ordering = ('-opened_at',)

    def __str__(self):
        return f"CashSession {self.pk} ({self.estado}) - {self.cash_register.nombre}"