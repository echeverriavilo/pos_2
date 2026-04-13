from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager


class DiningTable(models.Model):
    class States(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        OCUPADA = 'OCUPADA', 'Ocupada'
        PAGANDO = 'PAGANDO', 'Pagando'
        RESERVADA = 'RESERVADA', 'Reservada'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='dining_tables',
    )
    numero = models.CharField(max_length=32)
    estado = models.CharField(max_length=32, choices=States.choices, default=States.DISPONIBLE)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('tenant', 'numero')
        unique_together = (('tenant', 'numero'),)

    def __str__(self):
        return f"Mesa {self.numero} ({self.tenant.slug})"
