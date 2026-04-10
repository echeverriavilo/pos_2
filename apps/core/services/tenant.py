from decimal import Decimal

from django.db import transaction

from apps.core.models import Role, Tenant

BASE_ROLES = ['administrador', 'cajero', 'garzón']


class TenantService:
    @classmethod
    def create_tenant(cls, *, slug: str, name: str, config_iva: Decimal = Decimal('0.19'), config_flujo_mesas: bool = False) -> Tenant:
        slug = slug.lower()
        with transaction.atomic():
            tenant = Tenant.objects.create(
                slug=slug,
                name=name,
                config_iva=config_iva,
                config_flujo_mesas=config_flujo_mesas,
            )
            cls._seed_roles(tenant)
            return tenant

    @classmethod
    def _seed_roles(cls, tenant: Tenant):
        roles = []
        for name in BASE_ROLES:
            roles.append(Role(tenant=tenant, name=name))
        Role.objects.bulk_create(roles)

    @staticmethod
    def get_base_roles():
        return BASE_ROLES
