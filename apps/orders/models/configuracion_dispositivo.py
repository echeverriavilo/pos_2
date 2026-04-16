from django.core.exceptions import ValidationError
from django.db import models

from apps.catalog.models import Category
from apps.catalog.models import Product
from apps.core.models import Tenant
from apps.core.models.managers import TenantAwareManager
from apps.orders.models.dispositivo import Dispositivo


class ConfiguracionDispositivo(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='configuraciones_dispositivo',
    )
    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.CASCADE,
        related_name='configuraciones',
    )
    producto = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='+',
        null=True,
        blank=True,
    )
    categoria = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='+',
        null=True,
        blank=True,
    )
    prioridad = models.IntegerField(default=0)

    objects = TenantAwareManager()

    class Meta:
        ordering = ('tenant', '-prioridad')
        unique_together = (
            ('tenant', 'dispositivo', 'producto'),
            ('tenant', 'dispositivo', 'categoria'),
        )
        verbose_name = 'Configuración de Dispositivo'
        verbose_name_plural = 'Configuraciones de Dispositivos'

    def clean(self):
        super().clean()
        if self.producto and self.categoria:
            raise ValidationError('Debe especificar producto XOR categoría (no ambos).')
        if not self.producto and not self.categoria:
            raise ValidationError('Debe especificar producto XOR categoría (uno de los dos).')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        target = self.producto or self.categoria
        return f"{self.dispositivo.nombre} → {target} (prioridad: {self.prioridad})"