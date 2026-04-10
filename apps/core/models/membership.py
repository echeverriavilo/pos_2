from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models.role import Role
from apps.core.models.tenant import Tenant


class Membership(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='membership',
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='memberships',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def clean(self):
        if self.role and self.role.tenant_id != self.tenant_id:
            raise ValidationError('El rol debe pertenecer al mismo tenant que la membresía.')

    def __str__(self):
        return f"{self.user.email} -> {self.tenant.slug} ({self.role and self.role.name})"
