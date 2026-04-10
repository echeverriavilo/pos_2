from __future__ import annotations

from typing import Optional

from django.conf import settings

from apps.core.models import Tenant


def extract_tenant_slug(host: str, default_domain: str | None = None) -> Optional[str]:
    if not host:
        return None
    host = host.split(':')[0]
    default_domain = default_domain or settings.TENANT_DEFAULT_DOMAIN
    if default_domain and host == default_domain:
        return None
    if default_domain and host.endswith(f'.{default_domain}'):
        trimmed = host[: -len(f'.{default_domain}')]
        return trimmed.split('.')[0] if trimmed else None
    parts = host.split('.')
    if len(parts) > 1:
        return parts[0]
    return host


def get_tenant_by_slug(slug: str) -> Optional[Tenant]:
    if not slug:
        return None
    return Tenant.objects.filter(slug=slug).first()
