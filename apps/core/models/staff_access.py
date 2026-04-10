from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models.tenant import Tenant


class StaffTenantAccess(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_tenant_access',
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='staff_access',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'tenant'),)
        verbose_name = 'Staff Tenant Access'
        verbose_name_plural = 'Staff Tenant Accesses'

    def clean(self):
        if not self.user.is_platform_staff:
            raise ValidationError('Solo users platform staff pueden tener acceso a múltiples tenants.')

    def __str__(self):
        return f"{self.user.email} ↔ {self.tenant.slug}"
