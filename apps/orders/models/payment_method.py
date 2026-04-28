from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager


class PaymentMethod(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='payment_methods',
    )
    nombre = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('orden', 'nombre')
        unique_together = ('tenant', 'nombre')

    def __str__(self):
        return f"{self.nombre} ({self.tenant.slug})"

    def save(self, *args, **kwargs):
        if self.pk and self.__dict__.get('tenant') is None:
            self.tenant = PaymentMethod.objects.select_related('tenant').get(pk=self.pk).tenant
        if self.tenant is None:
            raise ValueError('El método de pago debe pertenecer a un tenant válido.')
        super().save(*args, **kwargs)
