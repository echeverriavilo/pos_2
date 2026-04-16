from django.db import models

from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager


class Dispositivo(models.Model):
    class Tipo(models.TextChoices):
        IMPRESORA = 'IMPRESORA', 'Impresora'
        PANTALLA = 'PANTALLA', 'Pantalla'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='dispositivos',
    )
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('tenant', 'nombre')
        unique_together = (('tenant', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} ({self.tenant.slug})"