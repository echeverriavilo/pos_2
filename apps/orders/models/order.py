from decimal import Decimal

from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager


class Order(models.Model):
    class Flow(models.TextChoices):
        MESA = 'MESA', 'Mesa'
        RAPIDO = 'RAPIDO', 'Rápido'

    class States(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        PAGADO_PARCIAL = 'PAGADO_PARCIAL', 'Pagado parcial'
        COMPLETADO = 'COMPLETADO', 'Completado'
        ANULADO = 'ANULADO', 'Anulado'

    ACTIVE_STATES = {
        States.ABIERTO,
        States.CONFIRMADO,
        States.PAGADO_PARCIAL,
    }

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    tipo_flujo = models.CharField(max_length=16, choices=Flow.choices)
    table = models.ForeignKey(
        'dining.DiningTable',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    estado = models.CharField(max_length=32, choices=States.choices)
    total_bruto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    objects = TenantAwareManager()

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f"Order {self.pk} ({self.estado})"

    @property
    def is_active(self):
        return self.estado in self.ACTIVE_STATES
