from django.conf import settings

from apps.core import tenant_context
from apps.core.selectors import tenant as tenant_selector


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.default_domain = getattr(settings, 'TENANT_DEFAULT_DOMAIN', 'localhost')

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        slug = tenant_selector.extract_tenant_slug(host, self.default_domain)
        tenant = tenant_selector.get_tenant_by_slug(slug)
        request.tenant_slug = slug
        request.tenant = tenant
        tenant_context.set_current_tenant(tenant)
        try:
            response = self.get_response(request)
        finally:
            tenant_context.clear_current_tenant()
        return response
