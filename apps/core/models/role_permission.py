from django.db import models

from apps.core.models.permission import Permission
from apps.core.models.role import Role


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('role', 'permission'),)

    def __str__(self):
        status = "✓" if self.active else "✗"
        return f"{self.role.name} → {self.permission.codename} ({status})"