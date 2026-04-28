from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager


class CashRegister(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='cash_registers',
    )
    nombre = models.CharField(max_length=100)
    soporta_flujo_mesa = models.BooleanField(default=True)
    soporta_flujo_rapido = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('tenant', 'nombre')
        unique_together = ('tenant', 'nombre')

    def __str__(self):
        return f"{self.nombre} ({self.tenant.slug})"