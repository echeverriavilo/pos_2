from django.db import models

from apps.core.models.managers import TenantAwareManager
from apps.core.models.tenant import Tenant


class Role(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = (('tenant', 'name'),)
        ordering = ('name',)

    def __str__(self):
        return f"{self.name} @ {self.tenant.slug}"
