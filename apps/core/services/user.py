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

    @staticmethod
    def update_tenant_user(user: CustomUser, *, email=None, first_name=None, last_name=None, role: Role = None, password: str = None) -> CustomUser:
        """Actualiza los datos de un usuario del tenant y opcionalmente su rol.

        Parámetros:
        - user: usuario a actualizar.
        - email: nuevo email (opcional).
        - first_name: nuevo nombre (opcional).
        - last_name: nuevo apellido (opcional).
        - role: nuevo rol de membresía (opcional).
        - password: nueva contraseña (opcional).

        Retorna:
        - CustomUser actualizado.
        """
        with transaction.atomic():
            if email is not None and email != user.email:
                if CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
                    raise ValueError('El email ya está en uso.')
                user.email = email
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if password:
                user.set_password(password)
            user.save()
            if role is not None:
                membership = getattr(user, 'membership', None)
                if not membership:
                    raise ValueError('El usuario no tiene membresía en este tenant.')
                if role.tenant_id != membership.tenant_id:
                    raise ValueError('El rol debe pertenecer al mismo tenant.')
                membership.role = role
                membership.save(update_fields=['role'])
        return user

    @staticmethod
    def toggle_user_active(user: CustomUser) -> CustomUser:
        """Activa o desactiva un usuario."""
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return user
