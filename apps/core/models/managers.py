from django.db import models

from apps.core.tenant_context import get_current_tenant


class TenantAwareQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        if tenant is None:
            return self.none()
        return self.filter(tenant=tenant)


class TenantAwareManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is None:
            return queryset
        return queryset.filter(tenant=tenant)

    def for_tenant(self, tenant):
        return self.get_queryset().for_tenant(tenant)
