from django.db import transaction

from apps.core.models import CustomUser, Membership, Role, StaffTenantAccess


class UserService:
    @staticmethod
    def create_tenant_user(*, email: str, password: str, tenant, role: Role, **extra) -> CustomUser:
        if role.tenant_id != tenant.id:
            raise ValueError('El rol debe pertenecer al mismo tenant.')
        with transaction.atomic():
            user = CustomUser.objects.create_user(email=email, password=password, **extra)
            Membership.objects.create(user=user, tenant=tenant, role=role)
        return user

    @staticmethod
    def create_platform_staff(*, email: str, password: str, is_active: bool = True, **extra) -> CustomUser:
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            is_platform_staff=True,
            is_staff=True,
            is_active=is_active,
            **extra,
        )
        return user

    @staticmethod
    def grant_staff_access(user: CustomUser, tenant) -> StaffTenantAccess:
        if not user.is_platform_staff:
            raise ValueError('Solo platform staff puede acceder a múltiples tenants.')
        access, _ = StaffTenantAccess.objects.get_or_create(user=user, tenant=tenant)
        return access
