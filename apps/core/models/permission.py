from django.db import models


class Permission(models.Model):
    codename = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('codename',)

    def __str__(self):
        return self.codename