from django.db import transaction
from django.core.exceptions import ValidationError

from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission, Tenant


class RoleServiceError(Exception):
    pass


class RoleService:
    @classmethod
    def create_role(cls, *, tenant: Tenant, name: str, description: str = '') -> Role:
        """Crea un nuevo rol para un tenant.

        Parámetros:
        - tenant: tenant al que pertenece el rol.
        - name: nombre del rol.
        - description: descripción opcional.

        Retorna:
        - Role creado.

        Raises:
        - RoleServiceError si el nombre ya existe para ese tenant.
        """
        if Role.objects.filter(tenant=tenant, name=name).exists():
            raise RoleServiceError(f'El rol "{name}" ya existe para este tenant.')

        with transaction.atomic():
            role = Role.objects.create(tenant=tenant, name=name, description=description)
        return role

    @classmethod
    def update_role(cls, *, role: Role, name: str = None, description: str = None) -> Role:
        """Actualiza la metadata de un rol.

        Parámetros:
        - role: rol a actualizar.
        - name: nuevo nombre (opcional).
        - description: nueva descripción (opcional).

        Retorna:
        - Role actualizado.
        """
        if name is not None:
            if Role.objects.filter(tenant=role.tenant, name=name).exclude(pk=role.pk).exists():
                raise RoleServiceError(f'El rol "{name}" ya existe para este tenant.')
            role.name = name
        if description is not None:
            role.description = description
        role.save(update_fields=['name', 'description'] if name and description else ['name'] if name else ['description'])
        return role

    @classmethod
    def delete_role(cls, *, role: Role) -> None:
        """Elimina un rol.

        Parámetros:
        - role: rol a eliminar.

        Raises:
        - RoleServiceError si hay usuarios con este rol asignado.
        """
        if Membership.objects.filter(role=role).exists():
            raise RoleServiceError('No se puede eliminar un rol con usuarios asociados.')

        with transaction.atomic():
            RolePermission.objects.filter(role=role).delete()
            role.delete()

    @classmethod
    def add_permission(cls, *, role: Role, permission_codename: str, active: bool = True) -> RolePermission:
        """Agrega un permiso al rol.

        Parámetros:
        - role: rol al que se agrega el permiso.
        - permission_codename: codename del permiso.
        - active: si el permiso starts activo (default True).

        Retorna:
        - RolePermission creado o actualizado.
        """
        perm, _ = Permission.objects.get_or_create(
            codename=permission_codename,
            defaults={'description': f'Permiso para {permission_codename}'}
        )
        with transaction.atomic():
            rp, created = RolePermission.objects.get_or_create(role=role, permission=perm)
            if not created:
                if rp.active != active:
                    rp.active = active
                    rp.save(update_fields=['active', 'updated_at'])
            else:
                rp.active = active
                rp.save(update_fields=['active'])
        return rp

    @classmethod
    def remove_permission(cls, *, role: Role, permission_codename: str) -> None:
        """Quita un permiso del rol completamente.

        Parámetros:
        - role: rol del que se quita el permiso.
        - permission_codename: codename del permiso.
        """
        perm = Permission.objects.filter(codename=permission_codename).first()
        if not perm:
            return
        RolePermission.objects.filter(role=role, permission=perm).delete()

    @classmethod
    def toggle_permission(cls, *, role: Role, permission_codename: str) -> bool:
        """Invierte el estado activo/inactivo de un permiso.

        Parámetros:
        - role: rol al que pertenece el permiso.
        - permission_codename: codename del permiso.

        Retorna:
        - Nuevo valor de active (True si ahora está activo).
        """
        perm = Permission.objects.filter(codename=permission_codename).first()
        if not perm:
            raise RoleServiceError(f'Permiso "{permission_codename}" no existe.')

        rp = RolePermission.objects.filter(role=role, permission=perm).first()
        if not rp:
            raise RoleServiceError(f'El rol no tiene el permiso "{permission_codename}".')

        with transaction.atomic():
            rp.active = not rp.active
            rp.save(update_fields=['active', 'updated_at'])
        return rp.active

    @classmethod
    def activate_permission(cls, *, role: Role, permission_codename: str) -> RolePermission:
        """Activa un permiso previamente desactivado.

        Parámetros:
        - role: rol al que pertenece el permiso.
        - permission_codename: codename del permiso.

        Retorna:
        - RolePermission actualizado.
        """
        return cls.add_permission(role=role, permission_codename=permission_codename, active=True)

    @classmethod
    def deactivate_permission(cls, *, role: Role, permission_codename: str) -> RolePermission:
        """Desactiva un permiso sin eliminarlo.

        Parámetros:
        - role: rol al que pertenece el permiso.
        - permission_codename: codename del permiso.

        Retorna:
        - RolePermission actualizado.
        """
        perm = Permission.objects.filter(codename=permission_codename).first()
        if not perm:
            raise RoleServiceError(f'Permiso "{permission_codename}" no existe.')

        rp = RolePermission.objects.filter(role=role, permission=perm).first()
        if not rp:
            raise RoleServiceError(f'El rol no tiene el permiso "{permission_codename}".')

        with transaction.atomic():
            rp.active = False
            rp.save(update_fields=['active', 'updated_at'])
        return rp

    @classmethod
    def get_permissions(cls, role: Role, active_only: bool = False):
        """Lista los permisos de un rol.

        Parámetros:
        - role: rol del que se listan permisos.
        - active_only: si True, solo retorna permisos activos.

        Retorna:
        - Lista de Permission.
        """
        return role.get_permissions(active_only=active_only)

    @classmethod
    def get_active_permissions(cls, role: Role):
        """Lista solo permisos activos del rol."""
        return role.get_active_permissions()

    @classmethod
    def get_inactive_permissions(cls, role: Role):
        """Lista solo permisos desactivados del rol."""
        return role.get_inactive_permissions()

    @classmethod
    def has_permission(cls, role: Role, permission_codename: str, active_only: bool = True) -> bool:
        """Verifica si el rol tiene un permiso.

        Parámetros:
        - role: rol a verificar.
        - permission_codename: codename del permiso.
        - active_only: si True, considera solo permisos activos.

        Retorna:
        - True si tiene el permiso.
        """
        return role.has_permission(permission_codename, active_only=active_only)