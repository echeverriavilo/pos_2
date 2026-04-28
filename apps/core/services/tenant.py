from decimal import Decimal

from django.db import transaction

from apps.core.models import Permission, Role, RolePermission, Tenant

BASE_ROLES = ['administrador', 'cajero', 'garzón']

BASE_PAYMENT_METHODS = [
    'Efectivo',
    'Tarjeta Débito',
    'Tarjeta Crédito',
    'Transferencia',
]

ROLE_PERMISSIONS = {
    'administrador': [
        'create_order',
        'add_item',
        'remove_item',
        'register_payment',
        'manage_inventory',
        'manage_users',
        'manage_tables',
        'manage_cash_registers',
        'open_cash_session',
        'close_cash_session',
    ],
    'cajero': [
        'register_payment',
        'open_cash_session',
        'close_cash_session',
    ],
    'garzón': [
        'create_order',
        'add_item',
        'remove_item',
        'manage_tables',
    ],
}


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
            cls._seed_payment_methods(tenant)
            return tenant

    @classmethod
    def _seed_roles(cls, tenant: Tenant):
        roles = []
        for name in BASE_ROLES:
            roles.append(Role(tenant=tenant, name=name))
        created_roles = Role.objects.bulk_create(roles)

        for role in created_roles:
            perms = ROLE_PERMISSIONS.get(role.name, [])
            for perm_codename in perms:
                perm, _ = Permission.objects.get_or_create(codename=perm_codename)
                RolePermission.objects.get_or_create(role=role, permission=perm)

    @classmethod
    def _seed_payment_methods(cls, tenant: Tenant):
        from apps.orders.models import PaymentMethod
        payment_methods = []
        for idx, nombre in enumerate(BASE_PAYMENT_METHODS, start=1):
            payment_methods.append(PaymentMethod(tenant=tenant, nombre=nombre, orden=idx, activo=True))
        PaymentMethod.objects.bulk_create(payment_methods)

    @staticmethod
    def get_base_roles():
        return BASE_ROLES
