from django.db import models

from apps.core.models.managers import TenantAwareManager
from apps.core.models.permission import Permission
from apps.core.models.tenant import Tenant


class Role(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, default='')
    permissions = models.ManyToManyField(Permission, through='core.RolePermission')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = (('tenant', 'name'),)
        ordering = ('name',)

    def __str__(self):
        return f"{self.name} @ {self.tenant.slug}"

    def has_permission(self, codename: str, active_only: bool = True) -> bool:
        from apps.core.models import RolePermission
        rps = RolePermission.objects.filter(role=self, permission__codename=codename)
        if active_only:
            rps = rps.filter(active=True)
        return rps.exists()

    def get_permissions(self, active_only: bool = False):
        from apps.core.models import RolePermission
        rps = RolePermission.objects.filter(role=self)
        if active_only:
            rps = rps.filter(active=True)
        return [rp.permission for rp in rps]

    def get_active_permissions(self):
        from apps.core.models import RolePermission
        return [rp.permission for rp in RolePermission.objects.filter(role=self, active=True)]

    def get_inactive_permissions(self):
        from apps.core.models import RolePermission
        return [rp.permission for rp in RolePermission.objects.filter(role=self, active=False)]
