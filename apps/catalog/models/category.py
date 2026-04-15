from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager


class Category(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='categories',
    )
    nombre = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('nombre',)
        unique_together = (('tenant', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} ({self.tenant.slug})"
